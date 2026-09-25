"""Build the backend thesis with bounded figures and linked navigation.

Run from the repository root: .venv312/Scripts/python.exe thesis/report-2026-backend/build_pdf.py
Requires reportlab, markdown, beautifulsoup4, pillow and pymupdf.
Personal information in the Markdown remains the author's responsibility.
"""
from pathlib import Path
import re, html, textwrap, json
from urllib.parse import unquote, urlparse
from collections import Counter
import markdown
from bs4 import BeautifulSoup, NavigableString
from PIL import Image as PILImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    PageBreak, KeepTogether, Table, TableStyle, Image, Preformatted, CondPageBreak)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
AUTHOR = json.loads((HERE / 'author-details.json').read_text(encoding='utf-8'))
OUT = ROOT / 'output/pdf/FinalYearReport-2026-Backend.pdf'
TMP = ROOT / 'tmp/pdfs/backend-layout'
TMP.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
W, H = A4
M = 62
CW = W - 2*M
INK = colors.HexColor('#172B42')
BLUE = colors.HexColor('#EAF0F6')
GREY = colors.HexColor('#627183')
for name, file in [('Serif','times.ttf'),('Serif-Bold','timesbd.ttf'),('Serif-Italic','timesi.ttf'),('Serif-BoldItalic','timesbi.ttf'),('Sans','arial.ttf'),('Sans-Bold','arialbd.ttf'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Serif', normal='Serif', bold='Serif-Bold', italic='Serif-Italic', boldItalic='Serif-BoldItalic')
pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='Sans-Bold', italic='Sans', boldItalic='Sans-Bold')
styles = {}
def style(name, **kw):
    styles[name] = ParagraphStyle(name, **kw)
style('body',fontName='Serif',fontSize=11.5,leading=16,spaceAfter=8,alignment=TA_JUSTIFY,allowWidows=0,allowOrphans=0)
style('left',parent=styles['body'],alignment=TA_LEFT)
style('h1',fontName='Serif-Bold',fontSize=19,leading=23,textColor=INK,spaceAfter=20,keepWithNext=True)
style('h2',fontName='Serif-Bold',fontSize=14,leading=18,textColor=INK,spaceBefore=12,spaceAfter=7,keepWithNext=True)
style('h3',fontName='Serif-Bold',fontSize=12,leading=16,spaceBefore=10,spaceAfter=6,keepWithNext=True)
style('cell',fontName='Serif',fontSize=9.5,leading=12,spaceAfter=0,splitLongWords=True)
style('caption',fontName='Sans',fontSize=9,leading=12,textColor=INK,spaceBefore=5,spaceAfter=10)
style('toc',fontName='Serif',fontSize=10.5,leading=13,spaceAfter=0)
style('cover',fontName='Serif',fontSize=12,leading=18,alignment=TA_CENTER,spaceAfter=12)
style('coverTitle',parent=styles['cover'],fontName='Serif-Bold',fontSize=21,leading=27,textColor=INK)

def clean(s):
    return s.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u200b','').replace('\u2192',' -> ').replace('\u2282',' < ').replace('\u2714','Yes').replace('\u2713','Yes')

def inline(node):
    if isinstance(node,NavigableString): return html.escape(clean(str(node)))
    tag=node.name
    value=''.join(inline(c) for c in node.children)
    if tag in ['strong','b']: return '<b>'+value+'</b>'
    if tag in ['em','i']: return '<i>'+value+'</i>'
    if tag=='code': return '<font name="Mono" size="9">'+value+'</font>'
    if tag=='br': return '<br/>'
    if tag=='a' and node.get('href','').startswith(('http:','https:')): return '<link href="'+html.escape(node['href'],quote=True)+'" color="#254C78">'+value+'</link>'
    return value

def p(s, which='body'):
    s = s.replace('[STUDENT NAME]', html.escape(AUTHOR['name'])).replace('[COMPUTER NUMBER]', html.escape(AUTHOR['number']))
    for key, placeholder in [('degree','[DEGREE PROGRAMME]'),('supervisor','[SUPERVISOR NAME]'),('date','[DATE OF SUBMISSION]')]:
        if AUTHOR.get(key): s = s.replace(placeholder, html.escape(AUTHOR[key]))
    return Paragraph(s, styles[which])

def arrow(d,x1,y1,x2,y2):
    import math
    d.add(Line(x1,y1,x2,y2,strokeColor=GREY,strokeWidth=1))
    a=math.atan2(y2-y1,x2-x1)
    pts=[x2,y2,x2-6*math.cos(a-.45),y2-6*math.sin(a-.45),x2-6*math.cos(a+.45),y2-6*math.sin(a+.45)]
    d.add(Polygon(pts,fillColor=GREY,strokeColor=GREY))

def box(d,x,y,w,h,title,lines,fs=10):
    d.add(Rect(x,y,w,h,rx=4,ry=4,fillColor=colors.white,strokeColor=GREY,strokeWidth=.7))
    d.add(Rect(x,y+h-25,w,25,fillColor=BLUE,strokeColor=None))
    d.add(String(x+10,y+h-17,title,fontName='Sans-Bold',fontSize=10.5,fillColor=INK))
    for i,line in enumerate(lines): d.add(String(x+10,y+h-42-i*(fs+4),line,fontName='Sans',fontSize=fs,fillColor=INK))

def flow(items):
    bh=66; gap=25; height=len(items)*(bh+gap)-gap
    d=Drawing(CW,height)
    for i,(title,lines) in enumerate(items):
        y=height-(i+1)*bh-i*gap
        box(d,40,y,CW-80,bh,title,lines)
        if i: arrow(d,CW/2,y+bh+gap-2,CW/2,y+bh+2)
    return d

def schema(live=False):
    d=Drawing(CW,528)
    data={
      'USERS':['id : int [PK]','first_name : varchar','last_name : varchar','email : varchar [unique]','phone : varchar','password_hash : varchar','role : varchar','national_id : varchar','badge_number : varchar','is_active : boolean','created_at : timestamptz'],
      'REPORTS':['id : int [PK]','reported_by : int [FK users]','owner_name : varchar','license_plate : varchar','vehicle_make : varchar','vehicle_model : varchar','vehicle_color : varchar','vehicle_year : varchar','chassis_number : varchar','incident_date : '+('timestamp' if live else 'timestamptz'),'status : varchar','last_seen_location : text','description : text','report_date : timestamptz','resolved_date : timestamptz','resolved_by : int [FK users]'],
      'AUDIT_LOG':['id : int [PK]','performed_by : int [FK users, nullable]','action : varchar','target_table : varchar','target_id : int','timestamp : timestamptz'],
      'ALERTS':['id : int [PK]','report_id : int [FK reports, cascade]','location_spotted : text','camera_id : varchar','confidence_score : float','image_path : varchar','is_read : boolean','detected_at : timestamptz']}
    box(d,0,302,222,207,'USERS',data['USERS'],9)
    box(d,249,237,222,272,'REPORTS',data['REPORTS'],9)
    box(d,0,126,222,142,'AUDIT_LOG',data['AUDIT_LOG'],9)
    box(d,249,30,222,168,'ALERTS',data['ALERTS'],9)
    arrow(d,222,450,249,450)
    arrow(d,111,302,111,268)
    arrow(d,360,237,360,198)
    d.add(String(8,285,'1 user : many audit entries',fontName='Sans',fontSize=8.5,fillColor=INK))
    d.add(String(260,216,'1 report : many alerts',fontName='Sans',fontSize=8.5,fillColor=INK))
    d.add(String(0,14,'Users file and resolve reports (1 : many). PK = primary key; FK = foreign key.',fontName='Sans',fontSize=9,fillColor=INK))
    d.add(String(0,0,'timestamptz = timestamp with time zone; timestamp = without time zone.',fontName='Sans',fontSize=9,fillColor=INK))
    return d

def diagram(name):
    if name in ['04-system-design-2.png','backend-live-schema-1.png']: return schema(name.startswith('backend'))
    if name=='04-system-design-1.png':
        d=Drawing(CW,415)
        box(d,0,324,210,85,'Phone camera',['IP Webcam / MJPEG stream'])
        box(d,0,175,210,90,'Camera node',['plate_node.py','YOLOv8n + EasyOCR'])
        box(d,261,175,210,90,'FastAPI backend',['REST routers + JWT checks','ConnectionManager /alerts/ws'])
        box(d,261,324,210,85,'PostgreSQL',['Users, reports, alerts, audit log'])
        box(d,80,0,311,85,'React browser portals',['Reportee / Police / Admin','REST + JWT; WebSocket detections'])
        arrow(d,105,324,105,265)
        arrow(d,210,220,261,220)
        d.add(String(200,278,'POST /alerts/check-plate',fontName='Sans',fontSize=9,fillColor=INK))
        arrow(d,365,265,365,324)
        arrow(d,365,175,305,85)
        arrow(d,235,85,310,175)
        d.add(String(0,134,'Live feed: browser -> FastAPI proxy -> phone camera',fontName='Sans',fontSize=9,fillColor=INK))
        return d
    if name=='04-system-design-3.png':
        return flow([
          ('1  Browser -> FastAPI',['POST /auth/login with email and password.']),
          ('2  FastAPI -> PostgreSQL',['Find the user by email; verify the bcrypt password hash.']),
          ('3  Credential and account checks',['Invalid credentials: 401. Deactivated account: 403.','Continue only for valid credentials and an active account.']),
          ('4  Successful authentication',['Write a login audit entry; return JWT, role and redirect.']),
          ('5  Browser session',['Store the token; the route guard reads its role.','Later API requests attach the token as a Bearer credential.'])])
    if name=='04-system-design-4.png':
        return flow([
          ('1  Camera node -> API',['POST /alerts/check-plate: plate, camera, confidence, location.']),
          ('2  API -> PostgreSQL',['Normalise the plate; search reports with status missing.','No matching report: return CLEAR to the camera node.']),
          ('3  Match found',['Insert an alert linked to the matching report.']),
          ('4  API -> ConnectionManager -> Police browser',['Broadcast STOLEN_DETECTED over the open WebSocket.','Payload includes the plate, location, camera and vehicle.']),
          ('5  API -> Camera node',['Return STOLEN with alert_id and the vehicle details.'])])
    if name=='backend-token-check-1.png':
        return flow([
          ('1  Validate the request token',['Check the JWT signature and expiry.']),
          ('2  Read the current database user',['Find the user by ID; require an active account.','Missing or inactive user: 401 Unauthorized.']),
          ('3  Apply the current role',['Read the role from the database row.','Role not allowed for this route: 403 Forbidden.']),
          ('4  Execute the route',['Continue only after the identity and role checks pass.'])])
    if name=='04-system-design-5.png':
        d=Drawing(CW,310)
        box(d,66,230,340,75,'Signed-in browser',['Route guards select the role-based portal.'])
        for x,title,lines in [(0,'Reportee - /my',['Home','Report Vehicle','My Reports','Profile']), (162,'Police - /police',['Home / Alerts','Cameras / Analytics','+ reportee functions']), (324,'Admin - /admin',['Users','System Health','Audit Log','+ police functions'])]:
            box(d,x,35,147,140,title,lines,9)
            arrow(d,CW/2,230,x+73,175)
        d.add(String(0,8,'The API independently checks the current database user and permitted role.',fontName='Sans',fontSize=9,fillColor=INK))
        return d
    return None

class Report(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=55,bottomMargin=55,title='SVDS - Backend, Database and Security Report',author=AUTHOR['name'])
        self.addPageTemplates(PageTemplate(id='report',frames=[Frame(M,55,CW,H-110,id='main',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.footer))
        self.entries=[]; self.chapter=''; self.body_start=None; self.last_level=0
    def label(self):
        if self.body_start: return str(self.page-self.body_start+1)
        n=self.page-1
        s=''
        for v,c in [(100,'c'),(90,'xc'),(50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]:
            while n>=v: s+=c;n-=v
        return s
    def footer(self,c,doc):
        if self.page==1:return
        c.saveState(); c.setStrokeColor(colors.HexColor('#CBD3DB')); c.line(M,43,W-M,43)
        c.setFillColor(GREY); c.setFont('Sans',8)
        c.drawString(M,30,'SVDS | Backend, Database and Security')
        # Draw the number in afterPage, after Chapter 1 establishes the body offset.
        c.restoreState()
    def afterPage(self):
        if self.page>1:
            self.canv.setFont('Sans',9);self.canv.setFillColor(INK);self.canv.drawRightString(W-M,30,self.label())
            self.canv.linkAbsolute('Contents','nav-contents',Rect=(M,20,M+210,40),thickness=0)
    def afterFlowable(self,f):
        if not hasattr(f,'nav'):return
        kind,level,title,key=f.nav
        if title.startswith('Chapter 1:') and self.body_start is None:self.body_start=self.page
        self.canv.bookmarkPage(key)
        if kind=='heading':
            self.canv.addOutlineEntry(title,key,level=level,closed=level>0)
        self.entries.append((kind,level,title,key,self.label(),self.page))

def build_story(previous):
    story=[]; keys=Counter(); table_counts=Counter(); chapter=''; last_heading=''; last_caption=None
    def heading(title,level=0,key=None,newpage=False):
        nonlocal chapter,last_heading
        if newpage: story.append(PageBreak())
        if level==0:
            m=re.match(r'(?:Chapter |Appendix )([\dA-G]+)',title)
            chapter=m.group(1) if m else 'P'
        last_heading=title
        keys['h']+=1; key=key or 'heading-'+str(keys['h'])
        q=p(html.escape(clean(title)), 'h'+str(min(level+1,3)));q.nav=('heading',level,clean(title),key);story.append(q)
    def caption(title,kind,key):
        q=p(html.escape(clean(title)),'caption');q.nav=(kind,0,clean(title),key);return q
    def navigation(title,key,kind):
        heading(title,key=key,newpage=True)
        rows=[]
        for k,lev,title,dest,label,physical in previous:
            if k!=kind or (kind=='heading' and (lev>1 or dest=='nav-contents')):continue
            indent='&#160;'*4 if lev else ''
            weight='<b>{}</b>' if lev==0 and kind=='heading' else '{}'
            text=weight.format(html.escape(title))
            rows.append([p(indent+'<link href="#'+dest+'">'+text+'</link>','toc'),p('<link href="#'+dest+'">'+label+'</link>','toc')])
        if not rows:rows=[[p('Navigation is generated during the build.','toc'),p('','toc')]]
        t=Table(rows,colWidths=[CW-35,35],hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.append(t)
    # Cover deliberately has no page number.
    for line in ['THE UNIVERSITY OF ZAMBIA','SCHOOL OF NATURAL AND APPLIED SCIENCES','DEPARTMENT OF COMPUTING AND INFORMATICS']:
        story.append(p('<b>'+line+'</b>','cover'))
    story.append(Spacer(1,35));story.append(p('FINAL YEAR PROJECT REPORT<br/>ACADEMIC YEAR 2026','cover'))
    story.append(Spacer(1,24));story.append(p('SVDS: A Camera-Based Stolen Vehicle Detection System for the Zambia Police Service','coverTitle'))
    story.append(p('The Backend, Database and Security Component','cover'))
    story.append(Spacer(1,25));story.append(p('A Final Year Project Report Submitted to the<br/>Department of Computing and Informatics<br/>in partial fulfilment of the requirements for the award of','cover'))
    story.append(p('[DEGREE PROGRAMME]','cover'));story.append(Spacer(1,22))
    story.append(p('Student Name: [STUDENT NAME]<br/>Computer Number: [COMPUTER NUMBER]<br/>Supervisor: [SUPERVISOR NAME]<br/>Date of Submission: [DATE OF SUBMISSION]','cover'))
    heading('DECLARATION',newpage=True)
    story.append(p('I declare that this final year project report is my own work and has been prepared in accordance with the academic requirements of the University of Zambia. All sources of information, ideas, data, software, images, and other material that are not my own have been appropriately acknowledged and referenced.'))
    story.append(p("Where this project was undertaken as part of a group, I have clearly identified my individual contributions and have not presented the work of other group members as my own."))
    for label in ['Student Name','Computer Number','Signature','Date']:
        value={'Student Name':AUTHOR['name'],'Computer Number':AUTHOR['number']}.get(label,'__________________________________________________')
        story.extend([Spacer(1,18),p('<b>'+label+':</b> '+html.escape(value),'left')])
    heading('APPROVAL',newpage=True)
    story.append(p('This final year project report has been submitted for examination with the approval of the project supervisor.'))
    for label in ['Supervisor Name','Signature','Date','Departmental/Examiner Approval (if applicable)']:
        story.extend([Spacer(1,20),p('<b>'+label+'</b>','left'),p('____________________________________________________________','left')])

    def image_flow(node):
        path=(HERE/node['src']).resolve();name=path.name;title=node.get('alt','Figure')
        keys['fig']+=1;key='figure-'+str(keys['fig'])
        d=diagram(name)
        if d is not None:
            d.__dict__['keepWithNext']=True
            story.extend([d,caption(title,'figure',key)]);return
        if name=='swagger-docs.png':
            im=PILImage.open(path)
            # Break only between endpoint groups: complete panels, no sliced rows.
            cuts=[310,986,1966,2830,3893]
            for i,(a,b) in enumerate(zip(cuts,cuts[1:])):
                # Omit the empty right side and collapse controls, retaining all route labels.
                piece=im.crop((0,a,800,b));dst=TMP/f'swagger-{i+1}.png';piece.save(dst)
                iw=CW;ih=iw*piece.height/piece.width
                cap=title+f' - detail panel {i+1} of 4'
                parts=[]
                if i==0:
                    header=TMP/'swagger-header.png';im.crop((0,0,im.width,310)).save(header)
                    parts.append(Image(str(header),width=CW,height=CW*310/im.width))
                parts.extend([Image(str(dst),width=iw,height=ih),caption(cap,'figure',key+'-'+str(i))])
                story.append(KeepTogether(parts))
            return
        im=PILImage.open(path);ratio=min(CW/im.width,560/im.height)
        story.append(KeepTogether([Image(str(path),width=im.width*ratio,height=im.height*ratio),caption(title,'figure',key)]))

    def parse(source):
        nonlocal last_caption
        soup=BeautifulSoup(markdown.markdown(source,extensions=['tables','fenced_code','sane_lists']),'html.parser')
        for n in soup.children:
            if isinstance(n,NavigableString):continue
            txt=n.get_text(' ',strip=True)
            signature=re.match(r'^(Computer Number|Signature|Date|Supervisor Name):\s*_',txt)
            if signature:
                story.append(p('<b>'+signature[1]+':</b> ______________________________________________','left'))
                continue
            if n.name in ['h1','h2','h3','h4']:
                heading(txt,min(int(n.name[1])-1,2),newpage=n.name=='h1');continue
            if n.name=='div' and 'plain-title' in n.get('class',[]):
                heading(txt,newpage=True);continue
            if n.name=='img':image_flow(n);continue
            if n.name=='p' and n.find('img'):image_flow(n.find('img'));continue
            if re.match(r'^Figure 4\.3:',txt):continue # caption generated from image alt
            if n.name=='p' and re.match(r'^Table \d+\.\d+:',txt):
                last_caption=txt;continue
            if n.name=='table':
                table_counts[chapter]+=1
                # Keep existing cited table numbers; newly captioned tables use section identifiers.
                desc=last_caption.split(':',1)[1].strip() if last_caption else re.sub(r'^(?:\d+(?:\.\d+)*|[A-G]\.\d+)\s+','',last_heading).capitalize()
                cap='Table '+chapter+'.'+str(table_counts[chapter])+': '+desc
                last_caption=None;keys['table']+=1
                cq=caption(cap,'table','table-'+str(keys['table']))
                rows=[]
                for tr in n.find_all('tr'):
                    cells=[]
                    for c in tr.find_all(['th','td']):
                        v=inline(c)
                        if c.name=='th':v='<b>'+v+'</b>'
                        cells.append(p(v,'cell'))
                    rows.append(cells)
                cols=len(rows[0]); weights=[1]*cols
                first=n.find('tr').get_text(' ',strip=True).lower()
                if cols==5:weights=[.80,1.12,2.0,1.55,1.03]
                elif cols==4:weights=[1.0,2.3,1.15,1.65]
                elif cols==3:weights=[1.2,2.5,2.3]
                elif cols==2:weights=[1.3,3.7]
                if 'columns' in first and 'rows' in first:weights=[.85,2.9,.45,1.8]
                if 'endpoint' in first and cols==5:weights=[.8,2.3,1.35,.8,1.05]
                if first.startswith('module lines'):weights=[1.65,.65,2.2,1.5]
                if 'suspected weakness' in first:weights=[.5,1.7,2.7,1.1]
                if 'result before' in first:weights=[.5,2.2,2.2,1.1]
                widths=[CW*x/sum(weights) for x in weights]
                t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT',splitByRow=1)
                t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),BLUE),('LINEBELOW',(0,0),(-1,0),.8,GREY),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#CBD3DB')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
                t.wrap(CW,700)
                minimum=sum(t._rowHeights[:2])+cq.wrap(CW,700)[1]+25
                heads=[]
                while story and hasattr(story[-1], 'nav') and story[-1].nav[0]=='heading':
                    head=story.pop();heads.insert(0,head);minimum+=head.wrap(CW,700)[1]+18
                story.extend([CondPageBreak(minimum),*heads,cq,t,Spacer(1,10)]);continue
            if n.name=='pre':
                lines=[]
                for line in clean(n.get_text()).splitlines():
                    lines.extend(textwrap.wrap(line,width=101,subsequent_indent='    ',replace_whitespace=False,drop_whitespace=False) or [''])
                ps=ParagraphStyle('code',fontName='Mono',fontSize=8.4,leading=11,spaceBefore=6,spaceAfter=10,backColor=colors.HexColor('#F3F5F7'),borderPadding=7)
                code=Preformatted('\n'.join(lines),ps)
                story.append(KeepTogether([code]) if len(lines)<=32 else code);continue
            if n.name in ['ul','ol']:
                for i,li in enumerate(n.find_all('li',recursive=False)):
                    ls=ParagraphStyle('list',parent=styles['left'],leftIndent=15,firstLineIndent=-12,spaceAfter=5)
                    prefix=str(i+1)+'.' if n.name=='ol' else '\u2022'
                    story.append(Paragraph(prefix+' '+inline(li),ls))
                continue
            if n.name=='hr':continue
            if txt:
                which='left' if chapter=='P' or txt.startswith(('Student Name:','Computer Number:','Signature:','Date:','Supervisor Name:')) else 'body'
                paragraph=p(inline(n),which)
                if txt.endswith(':'):paragraph.keepWithNext=True
                story.append(paragraph)

    front=(HERE/'front-matter.md').read_text(encoding='utf-8')
    # The detailed version note is retained as its own section, keeping the abstract together.
    start=front.index('**Note on the version')
    end=front.index('<div class="plain-title">ACKNOWLEDGEMENTS')
    version=front[start:end]
    front=front[:start]+front[end:]
    toc_start=front.index('<div class="plain-title">CONTENTS')
    abbr=front.index('<div class="plain-title">LIST OF ABBREVIATIONS')
    parse(front[:toc_start])
    navigation('CONTENTS','nav-contents','heading')
    navigation('LIST OF FIGURES','nav-figures','figure')
    navigation('LIST OF TABLES','nav-tables','table')
    parse(front[abbr:])
    heading('EVALUATED CODE VERSIONS',newpage=True);parse(version)
    for name in ['ch01-introduction.md','ch02-literature-review.md','ch03-methodology.md','ch04-analysis-design.md','ch05-implementation.md','ch06-testing-results.md','ch07-discussion.md','ch08-conclusion.md','references.md','appendix-a-contribution.md','appendix-b-to-g.md']:
        parse((HERE/name).read_text(encoding='utf-8'))
    return story

previous=[]
for run in range(6):
    doc=Report(TMP/'report.pdf')
    doc.build(build_story(previous))
    print(f'Pass {run+1}: {doc.page} pages, {len(doc.entries)} navigation entries')
    if previous==doc.entries:break
    previous=doc.entries
else:raise RuntimeError('Navigation did not converge')

# PDF page labels make viewer page navigation match the printed roman/Arabic numbers.
import pymupdf
pdf=pymupdf.open(TMP/'report.pdf')
pdf.set_page_labels([{'startpage':0,'prefix':'Cover','style':''},{'startpage':1,'prefix':'','style':'r','firstpagenum':1},{'startpage':doc.body_start-1,'prefix':'','style':'D','firstpagenum':1}])
pdf.save(OUT,garbage=4,deflate=True)
(TMP/'navigation.json').write_text(json.dumps(doc.entries,indent=2),encoding='utf-8')
print('Wrote',OUT)
