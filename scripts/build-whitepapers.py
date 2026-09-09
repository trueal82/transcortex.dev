#!/usr/bin/env python3
"""Regenerate the local PDFs. Requires reportlab and a DejaVu Sans font directory."""
from pathlib import Path
import argparse,json
from html import escape
from urllib.parse import quote,urlencode
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--font-dir',required=True);args=parser.parse_args()
fontdir=Path(args.font_dir)
pdfmetrics.registerFont(TTFont('LocalSans',str(fontdir/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('LocalSans-Bold',str(fontdir/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('LocalSans',normal='LocalSans',bold='LocalSans-Bold')
accent=colors.HexColor('#0f5d6b');ink=colors.HexColor('#1c1b1a');muted=colors.HexColor('#6b6862')
style={
 'body':ParagraphStyle('body',fontName='LocalSans',fontSize=9.4,leading=14,textColor=ink,spaceAfter=9),
 'title':ParagraphStyle('title',fontName='LocalSans-Bold',fontSize=27,leading=33,textColor=ink,spaceAfter=17),
 'h':ParagraphStyle('h',fontName='LocalSans-Bold',fontSize=15,leading=19,textColor=ink,spaceBefore=14,spaceAfter=10,keepWithNext=True),
 'eyebrow':ParagraphStyle('eyebrow',fontName='LocalSans-Bold',fontSize=8,leading=12,textColor=accent,spaceAfter=15),
 'lead':ParagraphStyle('lead',fontName='LocalSans',fontSize=12,leading=18,textColor=muted,spaceAfter=18),
 'small':ParagraphStyle('small',fontName='LocalSans',fontSize=8,leading=11.5,textColor=muted,spaceAfter=8),
}
def para(s,kind='body'):return Paragraph(escape(s).replace('\n','<br/>'),style[kind])
def footer(c,doc):
 c.setFont('LocalSans',8);c.setFillColor(muted);c.drawString(48,30,'Transcortex Labs · September 2026');c.drawRightString(A4[0]-48,30,f'{doc.page} / 5')
for lang in ('de','en'):
 de=lang=='de';data=json.loads((ROOT/'content/whitepapers'/f'{lang}.json').read_text());p=data['paragraphs'];story=[]
 def add(indices,heads=()):
  for i in indices:story.append(para(p[i],'h' if i in heads else 'body'))
 story+=[para('TRANSCORTEX LABS  /  WHITEPAPER','eyebrow'),Spacer(1,25),para(p[1],'title'),para(p[2],'lead'),para('September 2026 · '+('Für Geschäftsführung und Projektverantwortliche' if de else 'For managers and project owners'),'small'),Spacer(1,24)]
 add(range(8,11),[8])
 story+=[para('Ein sinnvoller Einstieg lässt sich prüfen.' if de else 'A useful starting point can be tested.','h'),para('Wählen Sie einen Ablauf, dessen Aufwand Sie kennen. Verbinden Sie passende Werkzeuge mit den Fähigkeiten Ihres Teams. Entscheiden Sie über den Ausbau anhand der Ergebnisse.' if de else 'Choose a process whose effort you understand. Connect suitable tools with your team’s skills. Use the results to decide whether to expand.'),Spacer(1,12)]
 steps=[['01','02','03'],['Prozess auswählen','Umsetzen und lernen','Nutzen messen'] if de else ['Choose a process','Implement and learn','Measure the value']]
 t=Table(steps,colWidths=[166,166,166]);t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'LocalSans'),('FONTNAME',(0,0),(-1,0),'LocalSans-Bold'),('TEXTCOLOR',(0,0),(-1,0),accent),('FONTSIZE',(0,0),(-1,0),18),('FONTSIZE',(0,1),(-1,1),8),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12),('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f1f5f4'))]));story+=[t,Spacer(1,20),para('In dieser Ausgabe: Forschung einordnen · Umsetzung planen · Beispielrechnung · Quellen' if de else 'Inside: research in context · implementation · illustrative business case · references','small'),PageBreak()]
 story.append(para('01 / '+('VOM POTENZIAL ZUR ANWENDUNG' if de else 'FROM POTENTIAL TO APPLICATION'),'eyebrow'));add(range(11,19),[11,14]);story.append(PageBreak())
 story.append(para('02 / '+('MENSCHEN UND ARBEITSABLÄUFE' if de else 'PEOPLE AND PROCESSES'),'eyebrow'));add(range(19,28),[19,22,25]);story.append(PageBreak())
 story+=[para('03 / '+('DEN EINSTIEG WIRTSCHAFTLICH PRÜFEN' if de else 'ASSESS THE BUSINESS CASE'),'eyebrow'),para('Eine Rechnung mit offenen Annahmen' if de else 'A calculation with explicit assumptions','h'),para('Illustratives Beispiel von Transcortex Labs, kein Angebot und kein Studienergebnis. Angenommen, die Bearbeitung einschließlich Nachprüfung sinkt bei 300 Vorgängen im Monat von 12 auf 5 Minuten.' if de else 'An illustrative example from Transcortex Labs, not a quote or a research finding. Suppose handling time, including review, falls from 12 to 5 minutes for 300 cases per month.')]
 rows=[('Freie Kapazität pro Monat','35 Stunden'),('Rechnerischer Kapazitätswert','35 × 40 € = 1.400 €/Monat'),('Angenommener laufender Aufwand','250 €/Monat'),('Angenommene einmalige Umsetzung','9.000 €')] if de else [('Capacity released per month','35 hours'),('Illustrative capacity value','35 × €40 = €1,400/month'),('Assumed running costs','€250/month'),('Assumed initial implementation','€9,000')]
 table=Table([[para(a),para(b)] for a,b in rows],colWidths=[249,249]);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f1f5f4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),7)]));story+=[table,Spacer(1,10),para('Bei zwölf vollen Nutzungsmonaten stehen einem rechnerischen Kapazitätswert von 16.800 € Kosten von 12.000 € gegenüber. Die Differenz von 4.800 € ist kein zugesicherter Gewinn: Freie Zeit wird erst wirtschaftlich wirksam, wenn sie sinnvoll genutzt werden kann. Mengen, tatsächliche Qualität, Einführung und interner Aufwand müssen in Ihre eigene Rechnung einfließen.' if de else 'Over twelve full months of use, an illustrative capacity value of €16,800 compares with costs of €12,000. The €4,800 difference is not a promised profit: released time creates economic value only when it can be used productively. Volumes, actual quality, rollout, and internal effort must be included in your own calculation.','small')]
 add(range(28,34),[28])
 maildata=json.loads((ROOT/'pages/contact-messages.json').read_text())['whitepaper'][lang]
 mail='mailto:info@transcortex.dev?'+urlencode(maildata,quote_via=quote)
 story.append(Paragraph('<a href="'+escape(mail,quote=True)+'" color="#0f5d6b">info@transcortex.dev</a>  ·  <a href="https://calendly.com/alexander-truemper" color="#0f5d6b">'+('Termin über Calendly' if de else 'Book via Calendly')+'</a>',style['body']))
 story.append(PageBreak())
 story+=[para('04 / '+('QUELLEN UND EINORDNUNG' if de else 'SOURCES AND CONTEXT'),'eyebrow'),para(p[35],'h'),para(p[36],'small')]
 for n in range(6):
  text=p[37+n]
  # Keep complete reference descriptions; attach their original source links.
  story.append(para(f'[{n+1}] '+text,'small'))
  links=' · '.join('<a href="'+escape(u,quote=True)+'" color="#0f5d6b">'+(('Quelle' if de else 'Source')+(' '+str(j+1) if len(data['references'][n])>1 else ''))+'</a>' for j,u in enumerate(data['references'][n]))
  story.append(Paragraph(links,style['small']));story.append(Spacer(1,7))
 story+=[Spacer(1,10),para('Webausgabe · September 2026. Die Beispielrechnung ist eine eigene Ergänzung. Die Studien untersuchen unterschiedliche Populationen und Zeiträume; ihre Ergebnisse sind keine pauschale Prognose für Ihr Unternehmen.' if de else 'Web edition · September 2026. The illustrative calculation is an editorial addition. The studies examine different populations and periods; their findings are not a general forecast for your business.','small')]
 out=ROOT/'assets/whitepapers'/f'transcortex-whitepaper-{lang}.pdf';out.parent.mkdir(parents=True,exist_ok=True)
 doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=49,title=p[1],author='Transcortex Labs',subject=p[2])
 doc.build(story,onFirstPage=footer,onLaterPages=footer)
 print(out)
