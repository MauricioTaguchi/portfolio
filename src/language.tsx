import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

export type Language = 'en' | 'pt';
type LanguageState = { language: Language; changeLanguage: (language: Language) => void };
const LanguageContext = createContext<LanguageState | null>(null);
const preferenceKey = 'portfolio-language-v1';

function initialLanguage(): Language {
  const requested = new URLSearchParams(window.location.search).get('lang');
  if (requested === 'en' || requested === 'pt') return requested;
  try { return localStorage.getItem(preferenceKey) === 'pt' ? 'pt' : 'en'; }
  catch { return 'en'; }
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(initialLanguage);
  useEffect(() => {
    const syncHistory = () => setLanguage(initialLanguage());
    window.addEventListener('popstate', syncHistory);
    return () => window.removeEventListener('popstate', syncHistory);
  }, []);
  function changeLanguage(next: Language) {
    setLanguage(next);
    const url = new URL(window.location.href);
    url.searchParams.set('lang', next);
    window.history.replaceState(null, '', url);
    try { localStorage.setItem(preferenceKey, next); } catch { /* The URL still preserves the choice. */ }
  }
  useEffect(() => {
    document.documentElement.lang = language === 'pt' ? 'pt-BR' : 'en';
    document.title = language === 'pt' ? 'Maurício Taguchi — Analista de Dados' : 'Maurício Taguchi — Data Analyst';
    const description = language === 'pt'
      ? 'Projetos e serviços freelance em análise de dados, SQL, Python, Power BI, qualidade de dados e automação.'
      : 'Projects and paid freelance services in data analytics, SQL, Python, Power BI, data quality and automation.';
    document.querySelector('meta[name="description"]')?.setAttribute('content', description);
  }, [language]);
  return <LanguageContext.Provider value={{ language, changeLanguage }}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('LanguageProvider is required');
  return context;
}

export function useTranslation() {
  const { language } = useLanguage();
  return (english: string, portuguese: string) => language === 'pt' ? portuguese : english;
}

export function LanguageSwitch() {
  const { language, changeLanguage } = useLanguage();
  return <div className="language-switch" role="group" aria-label={language === 'pt' ? 'Idioma do site' : 'Website language'}>
    <button type="button" lang="en" aria-label="English" aria-pressed={language === 'en'} onClick={() => changeLanguage('en')}>EN</button>
    <button type="button" lang="pt-BR" aria-label="Português do Brasil" aria-pressed={language === 'pt'} onClick={() => changeLanguage('pt')}>PT-BR</button>
  </div>;
}
