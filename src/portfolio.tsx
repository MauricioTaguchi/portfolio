import { useEffect, useRef, useState, type FormEvent } from 'react';
import { ArrowDown, ArrowUpRight, Check, Copy, Menu, X } from 'lucide-react';
import { Dialog, DialogContent, DialogTitle, DialogDescription, DialogTrigger, DialogClose } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';
import HeroPortrait from './portrait';
import { assetUrl } from './lib/assets';
import { LanguageProvider, LanguageSwitch, useLanguage, useTranslation } from './language';

const github = 'https://github.com/MauricioTaguchi';
const email = 'mailto:mauricioryotoitataguchi@gmail.com';
const linkedin = 'https://www.linkedin.com/in/mauriciotaguchi/';

function Navbar() {
  const [open, setOpen] = useState(false);
  const t = useTranslation();
  const navigation = [[t('About', 'Sobre'), '#sobre'], [t('Projects', 'Projetos'), '#projetos'], [t('Expertise', 'Competências'), '#expertise'], [t('Case studies', 'Estudos de caso'), assetUrl('case-studies/')], ['Blog', assetUrl('blog/')], [t('Contact', 'Contato'), '#contato']];
  return <header className="site-header">
    <a href="#inicio" className="wordmark" aria-label={t('Maurício Taguchi, home', 'Maurício Taguchi, início')}>TM<span>.</span></a>
    <nav aria-label={t('Main navigation', 'Navegação principal')}>{navigation.map(([name, href]) => <a key={href} href={href}>{name}</a>)}</nav>
    <div className="header-actions"><LanguageSwitch /><a className="header-cta" href="#contato">{t('Let’s talk', 'Vamos conversar')} <ArrowUpRight size={16} /></a></div>
    <Dialog open={open} onOpenChange={setOpen}><DialogTrigger asChild><button className="menu-button" aria-label={t('Open menu', 'Abrir menu')}><Menu size={23} /></button></DialogTrigger>
      <DialogContent className="mobile-menu" showCloseButton={false}>
        <DialogTitle className="sr-only">{t('Navigation menu', 'Menu de navegação')}</DialogTitle><DialogDescription className="sr-only">{t('Explore the sections of Maurício Taguchi’s portfolio.', 'Explore as seções do portfólio de Maurício Taguchi.')}</DialogDescription>
        <div className="mobile-menu-top"><span className="wordmark">TM<span>.</span></span><LanguageSwitch /><DialogClose asChild><button aria-label={t('Close menu', 'Fechar menu')}><X size={27} /></button></DialogClose></div>
        <nav aria-label={t('Mobile menu', 'Menu móvel')}>{navigation.map(([name, href], i) => <a key={href} href={href} onClick={() => setOpen(false)}><span aria-hidden="true">0{i + 1}</span>{name}<ArrowUpRight /></a>)}</nav>
        <p>{t('São Paulo, Brazil', 'São Paulo, Brasil')}<br />{t('Data, technology and curiosity.', 'Dados, tecnologia e curiosidade.')}</p>
      </DialogContent>
    </Dialog>
  </header>;
}

function Hero() {
  const t = useTranslation();
  return <section className="hero-track" aria-label={t('Introduction', 'Apresentação')}><div className="hero">
    <div className="hero-heading"><span className="eyebrow">{t('DATA ANALYTICS & BUSINESS INTELLIGENCE', 'ANÁLISE DE DADOS E BUSINESS INTELLIGENCE')}</span>
      <h1>{t('Data', 'Análise')}<br />{t('Analysis', 'de dados')}<br /><em>&amp; BI.</em></h1>
      <div className="freelance-intro"><strong>{t('Available for paid freelance projects', 'Disponível para projetos freelance remunerados')}</strong><span>{t('Data & BI · Python · SQL · Power BI', 'Dados e BI · Python · SQL · Power BI')}</span></div>
      <div className="hero-project-links">
        <a href={email} className="button-primary">{t('Discuss your project', 'Converse sobre seu projeto')} <ArrowUpRight size={19} /></a>
        <a href={assetUrl('demos/income/')} className="text-link">{t('Explore income by state', 'Explore a renda por estado')} <ArrowUpRight size={17} /></a>
        <a href={assetUrl('case-studies/brazil-income.html#power-bi-validation')} className="text-link">{t('Power BI report and 15 DAX checks', 'Relatório Power BI e 15 testes DAX')} <ArrowUpRight size={16} /></a>
      </div>
      <div className="hiring-links"><a href={assetUrl('resume/mauricio-taguchi-resume.pdf')} hrefLang="en" type="application/pdf" download>{t('Resume in English', 'Currículo em inglês')}</a><a href={assetUrl('resume/mauricio-taguchi-curriculo-pt.pdf')} hrefLang="pt-BR" type="application/pdf" download>{t('Resume in Portuguese', 'Currículo em português')}</a><a href={email}>{t('Email me', 'Envie um e-mail')}</a></div>
      <p className="availability">{t('Also open to data analytics & BI roles', 'Também aberto a vagas em Análise de Dados e BI')}<br />{t('São Paulo · Remote or hybrid', 'São Paulo · Remoto ou híbrido')}</p>
    </div>
    <HeroPortrait />
    <div className="hero-bio"><p className="small-label">{t('HELLO, I’M', 'OLÁ, SOU')}</p><h2>Maurício<br />Taguchi</h2><p className="role">{t('Data Analyst', 'Analista de Dados')}</p><span>{t('SQL, Python and Power BI', 'SQL, Python e Power BI')}</span><p className="hero-description">{t('At FIPE, I prepared economic and collective bargaining data for researchers and managers and helped build Power BI reports.', 'Na FIPE, preparei dados econômicos e de negociações coletivas para pesquisadores e gestores e participei da criação de relatórios em Power BI.')}</p><a href={github} target="_blank" rel="noreferrer" className="text-link">{t('My GitHub', 'Meu GitHub')} <ArrowUpRight size={16} /></a></div>
    <div className="hero-bottom"><span>{t('SÃO PAULO, BRAZIL', 'SÃO PAULO, BRASIL')}</span><a href="#sobre" className="scroll-hint">{t('SCROLL TO EXPLORE', 'EXPLORE O PORTFÓLIO')} <ArrowDown size={15} /></a><span>{t('PORTFOLIO / 2026', 'PORTFÓLIO / 2026')}</span></div>
  </div></section>;
}

function Projects() {
  const t = useTranslation();
  const projects = [
    { name: 'DataFlow', number: '02', category: t('DATA ENGINEERING & QUALITY', 'ENGENHARIA E QUALIDADE DE DADOS'), description: t('Check a spreadsheet before reporting.', 'Confira a planilha antes do relatório.'), body: t('Use a sample dataset to inspect missing or duplicate values, preview a change and undo it from the revision history.', 'Use uma base de exemplo para inspecionar valores ausentes ou duplicados, visualizar uma alteração e desfazê-la pelo histórico de revisões.'), stack: ['Python', 'FastAPI', 'React', 'PostgreSQL'], repo: 'data-analytics-platform', image: assetUrl('images/dataflow.webp'), cls: 'dataflow', alt: t('DataFlow interface with indicators and charts using demonstration data.', 'Interface do DataFlow com indicadores e gráficos usando dados de demonstração.') },
    { name: 'MarketPulse', number: '03', category: t('NEAR-REAL-TIME DATA', 'DADOS QUASE EM TEMPO REAL'), description: t('Markets move. So does the data.', 'O mercado se move. Os dados também.'), body: t('A cryptocurrency dashboard with WebSocket updates and pipeline health monitoring. From event ingestion to price, volume and latency visualization.', 'Um dashboard de criptomoedas com atualizações por WebSocket e monitoramento do pipeline. Da ingestão de eventos à visualização de preço, volume e latência.'), stack: ['Java', 'Spring Boot', 'React', 'Redis'], repo: 'marketpulse-live-dashboard', image: assetUrl('images/marketpulse.webp'), cls: 'marketpulse', alt: t('MarketPulse demonstration interface showing prices, volume and pipeline monitoring.', 'Interface de demonstração do MarketPulse com preços, volume e monitoramento do pipeline.') },
  ];
  return <section tabIndex={-1} id="projetos" className="section work"><div className="section-heading"><div><div className="section-label">{t('01 / SELECTED PROJECTS', '01 / PROJETOS SELECIONADOS')}</div><h2>{t('Selected work in', 'Projetos em')}<br /><span className="muted">{t('data and BI.', 'dados e BI.')}</span></h2></div><a className="text-link" href={github + '?tab=repositories'} target="_blank" rel="noreferrer">{t('All projects on GitHub', 'Todos os projetos no GitHub')} <ArrowUpRight size={17} /></a></div>
    <article className="income-project"><div className="income-intro"><span className="project-index">/01</span><span className="small-label">{t('ANALYTICS & BI', 'ANÁLISE DE DADOS E BI')}</span><h3>{t('Income Analysis', 'Análise de Renda')}<br />{t('in Brazil', 'no Brasil')}<span>.</span></h3>
      <p>{t('How does average income change when you select the Southeast? Explore 20 quarters of IBGE/SIDRA data and compare monthly earnings across Brazil’s 27 federal units.', 'Como a renda média muda ao selecionar o Sudeste? Explore 20 trimestres de dados do IBGE/SIDRA e compare os rendimentos mensais nas 27 unidades federativas.')}</p>
      <div className="stack"><span>Power BI</span><span>DAX</span><span>SQL</span><span>Python</span></div><div className="income-actions"><a href={assetUrl('demos/income/')} className="text-link">{t('Explore the dashboard', 'Explore o dashboard')} <ArrowUpRight size={17} /></a><a href={assetUrl('case-studies/brazil-income.html')} className="text-link">{t('Read income case study', 'Leia o estudo de renda')} <ArrowUpRight size={17} /></a></div>
    </div><div className="income-comparison"><span className="small-label">{t('REAL MONTHLY EARNINGS · Q1 2026', 'RENDIMENTO MENSAL REAL · 1º TRI. 2026')}</span><dl><div><dt>{t('All 27 federal units', 'Todas as 27 unidades federativas')}</dt><dd>{t('R$3,437.41', 'R$ 3.437,41')}</dd></div><div><dt>{t('Southeast · 4 states', 'Sudeste · 4 estados')}</dt><dd>{t('R$3,971.50', 'R$ 3.971,50')}</dd></div></dl><p>{t('Each federal unit carries equal weight. The Southeast mean was R$534.09 higher.', 'Cada unidade federativa tem o mesmo peso. A média do Sudeste foi R$ 534,09 maior.')}</p></div></article>
    {projects.map(project => <article className={'project ' + project.cls} key={project.repo}><a href={github + '/' + project.repo} target="_blank" rel="noreferrer" className="project-visual" data-cursor={t('VIEW', 'VER')} aria-label={t('View ', 'Ver ') + project.name + t(' on GitHub', ' no GitHub')}><div className="project-visual-top"><span>{project.name}</span><ArrowUpRight size={25} /></div><div className="project-screen"><img src={project.image} alt={project.alt} loading="lazy" width={project.cls === 'dataflow' ? 1266 : 1488} height={project.cls === 'dataflow' ? 712 : 1380} /></div><span className="image-caption">{t('PROJECT INTERFACE · DEMONSTRATION DATA', 'INTERFACE DO PROJETO · DADOS DE DEMONSTRAÇÃO')}</span></a><div className="project-info"><div className="project-title"><span className="project-index">/{project.number}</span><h3>{project.name}</h3><span className="project-category">{project.category}</span></div><div className="project-copy"><h4>{project.description}</h4><p>{project.body}</p><div className="project-end"><div className="stack">{project.stack.map(item => <span key={item}>{item}</span>)}</div><a className="text-link" href={github + '/' + project.repo} target="_blank" rel="noreferrer">{t('View project', 'Ver projeto')} <ArrowUpRight size={16} /></a>{project.repo === 'data-analytics-platform' ? <a className="text-link" href={assetUrl('case-studies/dataflow.html')}>{t('Read case study', 'Ler estudo de caso')} <ArrowUpRight size={16} /></a> : null}</div></div></div></article>)}
  </section>;
}

function About() {
  const t = useTranslation();
  return <><section id="sobre" className="section about"><div className="section-label">{t('02 / ABOUT ME', '02 / SOBRE MIM')}</div><div className="about-grid"><h2>{t('Beyond the numbers,', 'Além dos números,')}<br /><span className="muted">{t('the right questions.', 'as perguntas certas.')}</span></h2><div className="about-copy"><p className="lead">{t('I’m Maurício Taguchi, a Computer Science graduate driven by curiosity about how things work.', 'Sou Maurício Taguchi, formado em Ciência da Computação e movido pela curiosidade de entender como as coisas funcionam.')}</p><p>{t('At FIPE, I handled data quality checks for collective bargaining reports. I investigated inconsistent records, consolidated the data, and documented how I validated it. Researchers and managers used the resulting dataset to analyze trends and prepare reports.', 'Na FIPE, realizei verificações de qualidade de dados para relatórios de negociações coletivas. Investiguei registros inconsistentes, consolidei os dados e documentei as validações. Pesquisadores e gestores usaram a base resultante para analisar tendências e preparar relatórios.')}</p><p>{t('Since August 2026, I offer freelance services in data preparation, dashboards and automation. I also bring analytics, engineering and development together in personal projects.', 'Desde agosto de 2026, ofereço serviços freelance de preparação de dados, dashboards e automação. Também reúno análise, engenharia e desenvolvimento em projetos pessoais.')}</p><a href={linkedin} className="text-link" target="_blank" rel="noreferrer">{t('Explore my background', 'Conheça minha trajetória')} <ArrowUpRight size={17} /></a></div></div><div className="credentials"><div><span className="small-label">{t('EXPERIENCE', 'EXPERIÊNCIA')}</span><strong>FIPE</strong><p>{t('Data Analysis Internship', 'Estágio em Análise de Dados')}<br />{t('Jun. 2024 — Dec. 2025', 'Jun. 2024 — Dez. 2025')}</p></div><div><span className="small-label">{t('EDUCATION', 'FORMAÇÃO')}</span><strong>{t('Computer Science', 'Ciência da Computação')}</strong><p>{t('Bachelor’s degree · UNIP · 2026', 'Bacharelado · UNIP · 2026')}</p></div><div><span className="small-label">{t('FOCUS', 'FOCO')}</span><strong>{t('Data → Decisions', 'Dados → Decisões')}</strong><p>{t('Quality, automation and visualization', 'Qualidade, automação e visualização')}</p></div></div></section><div className="marquee" aria-hidden="true"><div>{[0, 1].map(i => <span key={i}>{t('DATA ANALYTICS', 'ANÁLISE DE DADOS')} <i>✳</i> PYTHON &amp; SQL <i>✳</i> BUSINESS INTELLIGENCE <i>✳</i> {t('AUTOMATION', 'AUTOMAÇÃO')} <i>✳</i> </span>)}</div></div></>;
}

function Expertise() {
  const t = useTranslation();
  const skills = [
    { name: t('Analytics & BI', 'Análise de Dados e BI'), tools: 'Power BI · DAX · Excel · Pandas · R', text: t('Indicators with context. Modeling, exploration and visualization to communicate what the data shows.', 'Indicadores com contexto. Modelagem, exploração e visualização para comunicar o que os dados mostram.') },
    { name: t('Data & Engineering', 'Dados e Engenharia'), tools: 'SQL · PostgreSQL · SQL Server · ETL', text: t('Reliable foundations. Source integration, preparation, modeling and validation before analysis.', 'Bases confiáveis. Integração de fontes, preparação, modelagem e validação antes da análise.') },
    { name: t('Code & Automation', 'Código e Automação'), tools: 'Python · FastAPI · Java · React · TypeScript', text: t('Simpler processes. Scripts, APIs and applications that connect data and eliminate repetitive steps.', 'Processos mais simples. Scripts, APIs e aplicações que conectam dados e eliminam etapas repetitivas.') },
    { name: t('Delivery & Tools', 'Entregas e Ferramentas'), tools: 'Git · GitHub Actions · Docker · Redis', text: t('Reproducible projects. Version control, documentation, tests and consistent environments.', 'Projetos reproduzíveis. Controle de versão, documentação, testes e ambientes consistentes.') },
  ];
  return <section id="expertise" className="section expertise"><div className="section-heading"><div><div className="section-label">{t('03 / EXPERTISE', '03 / COMPETÊNCIAS')}</div><h2>{t('Tools change.', 'As ferramentas mudam.')}<br /><span className="muted">{t('The goal is to solve.', 'O objetivo é resolver.')}</span></h2></div><p>{t('From exploration to delivery,', 'Da exploração à entrega,')}<br />{t('an end-to-end perspective.', 'uma visão do processo completo.')}</p></div><Accordion type="single" collapsible defaultValue="skill-0" className="skills-list">{skills.map((skill, i) => <AccordionItem key={i} value={'skill-' + i} className="skill-row"><AccordionTrigger className="skill-trigger"><span className="skill-index">0{i + 1}</span><span className="skill-name">{skill.name}</span><span className="skill-tools">{skill.tools}</span></AccordionTrigger><AccordionContent className="skill-content">{skill.text}</AccordionContent></AccordionItem>)}</Accordion></section>;
}

function Services() {
  const t = useTranslation();
  const services = [
    { name: t('Dashboards & BI', 'Dashboards e BI'), description: t('Clear indicators, structured models and reports designed for decision-makers.', 'Indicadores claros, modelos estruturados e relatórios para apoiar decisões.'), tools: 'Power BI · DAX · SQL' },
    { name: t('Process automation', 'Automação de processos'), description: t('Scripts and integrations that reduce repetitive work and create more room for analysis.', 'Scripts e integrações que reduzem tarefas repetitivas e abrem espaço para a análise.'), tools: 'Python · APIs · Excel' },
    { name: t('Pipelines & quality', 'Pipelines e qualidade'), description: t('From collection to validation: consistent data, traceable transformations and reproducible processes.', 'Da coleta à validação: dados consistentes, transformações rastreáveis e processos reproduzíveis.'), tools: 'Python · SQL · ETL' },
    { name: t('Data applications', 'Aplicações de dados'), description: t('Interfaces and APIs that turn analysis into tools people can use.', 'Interfaces e APIs que transformam análises em ferramentas para as pessoas usarem.'), tools: 'FastAPI · React · PostgreSQL' },
  ];
  return <section id="servicos" className="section services"><div className="section-label">{t('04 / HOW I CAN HELP', '04 / COMO POSSO AJUDAR')}</div><div className="services-heading"><h2>{t('Your next challenge.', 'Seu próximo desafio.')}<br /><em>{t('Let’s solve it.', 'Vamos resolver.')}</em></h2><p>{t('Clear communication.', 'Comunicação clara.')}<br />{t('Attention to quality.', 'Atenção à qualidade.')}<br />{t('Technology with purpose.', 'Tecnologia com propósito.')}</p></div><div className="service-list">{services.map((s, i) => <a href="#contato" key={i} className="service"><span className="service-number">0{i + 1}</span><div><h3>{s.name}</h3><p>{s.description}</p><span>{s.tools}</span></div><ArrowUpRight size={24} /></a>)}</div></section>;
}

function Contact() {
  const t = useTranslation();
  const { language } = useLanguage();
  const [topic, setTopic] = useState('data');
  const [prepared, setPrepared] = useState<{ name: string; email: string; message: string; topic: string } | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');
  const contactTopics = [
    { label: t('Data and BI', 'Dados e BI'), value: 'data', phrase: t('data and BI', 'dados e BI') },
    { label: t('Automation', 'Automação'), value: 'automation', phrase: t('automation', 'automação') },
    { label: t('Data pipeline', 'Pipeline de dados'), value: 'pipeline', phrase: t('a data pipeline', 'um pipeline de dados') },
    { label: t('Web application', 'Aplicação web'), value: 'web', phrase: t('a web application', 'uma aplicação web') },
    { label: t('Career opportunity', 'Oportunidade profissional'), value: 'career', phrase: t('a career opportunity', 'uma oportunidade profissional') },
    { label: t('Something else', 'Outro assunto'), value: 'other', phrase: t('something else', 'outro assunto') },
  ];
  const selected = prepared ? contactTopics.find(item => item.value === prepared.topic) : null;
  const message = prepared ? language === 'pt'
    ? `Olá, Maurício! Meu nome é ${prepared.name}.\n\nGostaria de conversar sobre ${selected?.phrase}.\n\n${prepared.message}\n\nMeu e-mail: ${prepared.email}`
    : `Hello, Maurício! My name is ${prepared.name}.\n\nI’d like to discuss ${selected?.phrase}.\n\n${prepared.message}\n\nMy email: ${prepared.email}` : '';
  function prepare(e: FormEvent<HTMLFormElement>) { e.preventDefault(); const data = new FormData(e.currentTarget); setPrepared({ name: String(data.get('name')), email: String(data.get('email')), message: String(data.get('message')), topic }); setCopied(false); setError(''); }
  async function copy() { try { await navigator.clipboard.writeText(message); setCopied(true); setError(''); } catch { setError(t('Select and copy the text below, or open it in your email app.', 'Selecione e copie o texto abaixo ou abra a mensagem no seu aplicativo de e-mail.')); } }
  useEffect(() => { setCopied(false); setError(''); }, [language]);
  const emailDraft = email + '?subject=' + encodeURIComponent(t('Project enquiry — ', 'Proposta de projeto — ') + (prepared?.name || '')) + '&body=' + encodeURIComponent(message);
  return <section id="contato" className="section contact"><div className="section-label">{t('05 / LET’S TALK', '05 / VAMOS CONVERSAR')}</div><div className="contact-grid"><div className="contact-intro"><h2>{t('Good projects', 'Bons projetos')}<br />{t('start with', 'começam com')}<br />{t('a conversation', 'uma conversa')}<span>.</span></h2><p>{t('Have a data challenge, a project idea or an opportunity? I’d like to hear about it.', 'Tem um desafio com dados, uma ideia de projeto ou uma oportunidade? Vamos conversar.')}</p><a className="contact-main-link" href={email}>{t('Email me', 'Envie um e-mail')} <ArrowUpRight size={27} /></a><div className="social-links"><a href={assetUrl('resume/')}>{t('Resume', 'Currículo')} <ArrowUpRight size={14} /></a><a href={linkedin} target="_blank" rel="noreferrer">LinkedIn <ArrowUpRight size={14} /></a><a href={github} target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={14} /></a></div></div>
    <div className="contact-form-wrap"><h3>{t('Tell me about your idea.', 'Conte sua ideia.')}</h3><p className="form-note">{t('Prepare your message, then open it in your email app or copy it to LinkedIn.', 'Prepare sua mensagem e abra no seu aplicativo de e-mail ou copie para o LinkedIn.')}</p><form onSubmit={prepare}><div className="form-pair"><label>{t('Your name', 'Seu nome')}<input name="name" autoComplete="name" required maxLength={100} placeholder={t('What should I call you?', 'Como posso chamar você?')} /></label><label>E-mail<input name="email" type="email" autoComplete="email" required maxLength={150} placeholder={t('you@company.com', 'voce@empresa.com')} /></label></div><label>{t('What would you like to discuss?', 'Sobre o que gostaria de conversar?')}<Select value={topic} onValueChange={setTopic}><SelectTrigger className="contact-select" aria-label={t('Project type', 'Tipo de projeto')}><SelectValue /></SelectTrigger><SelectContent>{contactTopics.map(({ label, value }) => <SelectItem key={value} value={value}>{label}</SelectItem>)}</SelectContent></Select></label><label>{t('Your message', 'Sua mensagem')}<textarea name="message" required minLength={10} maxLength={2500} rows={3} placeholder={t('What challenge would you like to solve?', 'Qual desafio você gostaria de resolver?')} /></label><button type="submit" className="contact-submit">{t('Prepare message', 'Preparar mensagem')} <ArrowUpRight size={20} /></button><p className="privacy-note">{t('This form does not send anything. Review and send the message in your email app or LinkedIn.', 'Este formulário não envia nada. Revise e envie a mensagem pelo seu aplicativo de e-mail ou LinkedIn.')}</p></form>
      {prepared ? <div className="prepared-message" role="status"><h4>{t('Your message is ready to copy', 'Sua mensagem está pronta')}</h4><textarea aria-label={t('Prepared message', 'Mensagem preparada')} value={message} readOnly rows={6} /><div><a className="open-email" href={emailDraft}>{t('Open email draft', 'Abrir rascunho de e-mail')} <ArrowUpRight size={16} /></a><button onClick={copy}>{copied ? <Check size={16} /> : <Copy size={16} />} {copied ? t('Copied', 'Copiada') : t('Copy message', 'Copiar mensagem')}</button><a href={linkedin} target="_blank" rel="noreferrer">{t('Open LinkedIn', 'Abrir LinkedIn')} <ArrowUpRight size={16} /></a></div>{error ? <p>{error}</p> : null}</div> : null}
    </div></div><footer><a href="#inicio" className="wordmark">TM<span>.</span></a><p>{t('Made with curiosity and code.', 'Feito com curiosidade e código.')}</p><span>© 2026 Maurício Taguchi</span><a href="#inicio" aria-label={t('Back to home', 'Voltar ao início')}><ArrowUpRight size={24} /></a></footer></section>;
}

function TechnicalWriting() {
  const t = useTranslation();
  return <aside className="technical-writing" aria-labelledby="technical-writing-title"><div><div><h2 id="technical-writing-title">{t('Technical articles', 'Artigos técnicos')}</h2><p>{t('Reproducible examples about Python, data and development.', 'Exemplos reproduzíveis sobre Python, dados e desenvolvimento.')}</p></div><a href={assetUrl('blog/')}>{t('Explore the blog', 'Explore o blog')}</a></div></aside>;
}

function Motion(){
const cursor=useRef<HTMLDivElement>(null);
useEffect(()=>{let cleanup=()=>{};let cancelled=false;const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
if(!reduce){Promise.all([import('gsap'),import('gsap/ScrollTrigger'),import('lenis')]).then(([g,s,l])=>{if(cancelled)return;g.gsap.registerPlugin(s.ScrollTrigger);const lenis=new l.default({duration:.9,anchors:{offset:-90},smoothWheel:true});lenis.on('scroll',s.ScrollTrigger.update);const raf=(time:number)=>lenis.raf(time*1000);g.gsap.ticker.add(raf);g.gsap.ticker.lagSmoothing(0);const ctx=g.gsap.context(()=>{g.gsap.utils.toArray<HTMLElement>('.section-heading, .about-grid, .credentials, .project-info, .services-heading').forEach(el=>g.gsap.from(el,{y:28,autoAlpha:0,duration:.75,ease:'power2.out',scrollTrigger:{trigger:el,start:'top 93%',once:true}}));});cleanup=()=>{ctx.revert();g.gsap.ticker.remove(raf);lenis.destroy();};});}
const el=cursor.current;const useCursor=matchMedia('(pointer:fine)').matches&&!reduce;
const move=(e:PointerEvent)=>{if(!el||!useCursor)return;el.style.transform=`translate3d(${e.clientX}px,${e.clientY}px,0)`;el.style.opacity='1';const target=(e.target as HTMLElement).closest('[data-cursor],a,button');el.classList.toggle('active',!!target);el.textContent=target?.getAttribute('data-cursor')??'';};const leave=()=>{if(el)el.style.opacity='0';};if(useCursor){document.addEventListener('pointermove',move,{passive:true});document.addEventListener('pointerleave',leave);}return()=>{cancelled=true;cleanup();document.removeEventListener('pointermove',move);document.removeEventListener('pointerleave',leave);};},[]);
return <div className="custom-cursor" ref={cursor} aria-hidden="true"/>;
}

export default function Portfolio(){return <LanguageProvider><PortfolioContent /></LanguageProvider>;}
function PortfolioContent(){const t=useTranslation();return <><a className="skip-link" href="#projetos">{t('Skip to projects','Ir para os projetos')}</a><Navbar/><main id="inicio"><Hero/><Projects/><About/><Expertise/><Services/><Contact/></main><Motion/><TechnicalWriting/></>;}
