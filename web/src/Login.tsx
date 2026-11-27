import { useEffect, useState } from "react";
import { api, type Account } from "./api";
import { useKept } from "./hooks";
import { Emblem } from "./About";
import { Forgot, TERMS_VERSION, TermsDialog } from "./Terms";

/** Sign in / create account, split in two, one screen tall. On the left, the painting of Krishna and Garuda in the temple
 *  garden; on the right, white: the invocation, the name and the form.
 *  Archived, still reachable at `?verses`: the first design, whose left half was black with one of three ślokas of refuge at
 *  a time, its lines rising in one after another (Rāma's vow, Rāmāyaṇa Yuddha 18.33; Krishna's last word to Arjuna, Gita
 *  18.66; the Lord to Aditi, Bhāgavatam 8.17.17). */

const VERSES = [
  {
    padas: ["सकृदेव प्रपन्नाय", "तवास्मीति च याचते ।", "अभयं सर्वभूतेभ्यो", "ददाम्येतद्व्रतं मम ॥ ३३ ॥"],
    iast: ["sakṛd eva prapannāya tavāsmīti ca yācate", "abhayaṃ sarva-bhūtebhyo dadāmy etad vrataṃ mama"],
    meaning: "To one who comes to Me even once, surrendering and pleading “I am Yours”, I grant freedom from fear of all beings. This is My vow.",
    cite: "Rāma to Sugrīva, Vālmīki Rāmāyaṇa, Yuddha Kāṇḍa 18.33",
    short: "Rāmāyaṇa",
  },
  {
    padas: ["सर्वधर्मान्परित्यज्य", "मामेकं शरणं व्रज ।", "अहं त्वा सर्वपापेभ्यो", "मोक्षयिष्यामि मा शुचः ॥ ६६ ॥"],
    iast: ["sarva-dharmān parityajya mām ekaṃ śaraṇaṃ vraja", "ahaṃ tvā sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ"],
    meaning: "Setting aside all dharmas, take refuge in Me alone. I shall free you from all sins; do not grieve.",
    cite: "Kṛṣṇa to Arjuna, Bhagavad Gītā 18.66",
    short: "Gītā",
  },
  {
    padas: ["अथाप्युपायो मम देवि चिन्त्यः", "सन्तोषितस्य व्रतचर्यया ते ।", "ममार्चनं नार्हति गन्तुमन्यथा", "श्रद्धानुरूपं फलहेतुकत्वात् ॥ १७ ॥"],
    iast: ["athāpy upāyo mama devi cintyaḥ santoṣitasya vrata-caryayā te", "mamārcanaṃ nārhati gantum anyathā śraddhānurūpaṃ phala-hetukatvāt"],
    meaning: "Pleased by the vow you have kept, O goddess, I will find a way to grant your wish, for worship of Me never goes in vain. It bears fruit as one’s faith deserves.",
    cite: "The Lord to Aditi, Śrīmad Bhāgavatam 8.17.17",
    short: "Bhāgavatam",
  },
];
type Tab = "in" | "up";

/** the garden look unless the URL asks for the archived verses one with `?verses` */
const GARDEN = !new URLSearchParams(location.search).has("verses");

/** The paintings the sign-in side shows, one after another, five seconds each; a dot click switches at once, with a quicker fade. */
const ART = [
  { src: "/krishna-cosmos.jpg", alt: "Krishna haloed among golden clouds under a great moon, lotuses at his feet" },
  { src: "/krishna-chakra-eyes.jpg", alt: "Krishna with golden eyes, the Sudarshana chakra spinning on his raised finger" },
  { src: "/krishna-runes.jpg", alt: "Eight-armed Krishna in black and white under an arc of the seven chakras, Om and a trident below" },
];

/** Sign in with a provider: a plain link to the server, which goes to the provider and comes back signed in (or with
 *  ?auth_error=… for the form to show). Brand marks in one ink, to keep the page monochrome. */
const SOCIAL = [
  { id: "google", label: "Google", paths: [
    "M23.49 12.27c0-.79-.07-1.54-.19-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58v3h3.86c2.26-2.09 3.56-5.17 3.56-8.82z",
    "M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.86-3c-1.08.72-2.45 1.16-4.07 1.16-3.13 0-5.78-2.11-6.73-4.96H1.29v3.09C3.26 21.3 7.31 24 12 24z",
    "M5.27 14.29c-.25-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29V6.62H1.29C.47 8.24 0 10.06 0 12s.47 3.76 1.29 5.38l3.98-3.09z",
    "M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.26 2.7 1.29 6.62l3.98 3.09c.95-2.85 3.6-4.96 6.73-4.96z"] },
  { id: "facebook", label: "Facebook", paths: [
    "M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"] },
  { id: "linkedin", label: "LinkedIn", paths: [
    "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"] },
  { id: "microsoft", label: "Microsoft", paths: [
    "M0 0h11.377v11.377H0zm12.623 0H24v11.377H12.623zM0 12.623h11.377V24H0zm12.623 0H24V24H12.623z"] },
] as const;

/** an error the server sent back from a provider's sign-in, read once and taken off the URL so a reload doesn't repeat it */
function takeAuthError() {
  const q = new URLSearchParams(location.search), text = q.get("auth_error");
  // the server always puts it last; cut just that, so ?verses stays ?verses (rebuilding the query would make it ?verses=)
  if (text) history.replaceState(null, "", location.pathname + location.search.replace(/[?&]auth_error=[^&]*$/, ""));
  return text ? { text } : null;
}

export function Login({ onDone, paused }: { onDone: (a: Account) => void; paused?: boolean }) {
  const [tab, setTab] = useKept<Tab>("login.tab", "in");
  const [verse, setVerse] = useState(0);
  const [art, setArt] = useState(0);
  const [quick, setQuick] = useState(false);
  useEffect(() => {
    if (paused) return;   // the intro is still over the page: the first slide's 5s start once it's seen
    const t = setTimeout(() => { setQuick(false); setArt((art + 1) % ART.length); }, 5_000);
    return () => clearTimeout(t);
  }, [art, paused]);
  const [busy, setBusy] = useState(false);
  const [reveal, setReveal] = useState(false);
  const [terms, setTerms] = useKept("login.terms", false);
  const [forgot, setForgot] = useKept("login.forgot", false);
  const [error, setError] = useState<{ text: string; taken?: boolean } | null>(takeAuthError);
  // the owner's login, prefilled only when the page is opened on the owner's Mac: the server sends none through the tunnel
  const [owner, setOwner] = useState<{ email: string; password: string } | null>(null);
  useEffect(() => { api.ownerLogin().then(setOwner, () => {}); }, []);
  const go = (t: Tab) => { setTab(t); setError(null); setReveal(false); setForgot(false); };

  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const d = new FormData(e.currentTarget), s = (k: string) => String(d.get(k) ?? "");
    setBusy(true); setError(null);
    try {
      onDone(tab === "in" ? await api.signIn(s("email"), s("password")) : await api.signUp(s("name"), s("email"), s("password"), s("username"), TERMS_VERSION));
    } catch (err) {
      const text = (err as Error).message;
      setError({ text, taken: text.startsWith("An account with this email") });
    } finally { setBusy(false); }
  };

  const verb = tab === "in" ? "Sign in" : "Create account";
  const v = VERSES[verse];
  return (
    <main className="vk" data-tab={tab} data-garden={GARDEN || undefined}>
      <div className="vk-side">
        {GARDEN && (
          <div className="vk-top">
            <p className="vk-invocation" lang="sa">॥ श्रीमते नारायणाय नमः ॥</p>
          </div>
        )}
        <div className="vk-form-box">
          <header className="vk-name">
            <div className="vk-lockup">
              <Emblem />
              <h1>Sudarshana</h1>
              <p lang="sa">सुदर्शन</p>
            </div>
          </header>
          <div className="vk-tabs" role="tablist" aria-label="Account">
            <button role="tab" aria-selected={tab === "in"} onClick={() => go("in")}>Sign in</button>
            <button role="tab" aria-selected={tab === "up"} onClick={() => go("up")}>Create account</button>
          </div>
          <form className="vk-form" key={tab + (owner ? "+" : "")} onSubmit={submit}>
            {tab === "up" && <label>Name<input name="name" autoComplete="name" required autoFocus /></label>}
            {tab === "up" && <label><span>Username <small className="muted">Optional</small></span><input name="username" autoComplete="username" /></label>}
            {tab === "in"
              ? <label>Email or username<input name="email" autoComplete="username" required defaultValue={owner?.email} /></label>
              : <label>Email<input name="email" type="email" autoComplete="email" required /></label>}
            <label><span>Password {tab === "up" && <small id="vk-pw-hint" className="muted">At least 8 characters</small>}</span>
              <span className="vk-pw">
              <input name="password" type={reveal ? "text" : "password"} required minLength={tab === "up" ? 8 : undefined} maxLength={256} defaultValue={tab === "in" ? owner?.password : undefined}
                autoComplete={tab === "in" ? "current-password" : "new-password"} aria-describedby={tab === "up" ? "vk-pw-hint" : undefined} />
              <button type="button" className="vk-reveal" aria-pressed={reveal} aria-label={reveal ? "Hide password" : "Show password"}
                onClick={() => setReveal(!reveal)}>{reveal ? "Hide" : "Show"}</button>
              </span>
            </label>
            {tab === "in" && <button type="button" className="link vk-forgot" aria-expanded={forgot} onClick={() => setForgot(!forgot)}>Forgot password?</button>}
            {tab === "in" && forgot && <p className="muted vk-forgot-note"><Forgot /></p>}
            <button className="primary" disabled={busy} autoFocus={tab === "in"}>{busy ? (tab === "in" ? "Signing in…" : "Creating account…") : <>{verb}{GARDEN && <span className="vk-arrow" aria-hidden="true">→</span>}</>}</button>
            {error && (
              <p role="alert" className="error vk-error">
                {error.text}{error.taken && <> <button type="button" className="link" onClick={() => go("in")}>Sign in instead</button></>}
              </p>
            )}
          </form>
          <div className="vk-or"><span>or continue with</span></div>
          <nav className="vk-social" aria-label="Sign in with another account">
            {SOCIAL.map((p) => (
              <a key={p.id} href={`/api/auth/oauth/${p.id}?back=${encodeURIComponent(location.search)}`} aria-label={`Continue with ${p.label}`}
                onClick={() => { try { sessionStorage.setItem("intro", "1"); } catch { /* blocked storage: no fade after this sign-in */ } }}>
                <svg viewBox="0 0 24 24" aria-hidden="true">{p.paths.map((d) => <path key={d} d={d} />)}</svg>
                <span>{p.label}</span>
              </a>
            ))}
          </nav>
          <p className="muted vk-terms">By continuing, you confirm you are 18 or older and agree to the <button type="button" className="link" onClick={() => setTerms(true)}>Terms of Service</button>, including the Privacy section.</p>
        </div>
      </div>
      <TermsDialog open={terms} onClose={() => setTerms(false)} />
      {GARDEN ? (
        <aside className="vk-art" data-quick={quick || undefined}>
          {ART.map((a, i) => <img key={a.src} src={a.src} alt={a.alt} aria-hidden={i !== art} data-on={i === art || undefined} />)}
          <nav className="vk-dots" aria-label="Paintings">
            {ART.map((a, i) => <button key={a.src} type="button" aria-label={`Painting ${i + 1}`} aria-current={i === art} onClick={() => { setQuick(true); setArt(i); }} />)}
          </nav>
        </aside>
      ) : <aside className="vk-verse" aria-label="Three verses of refuge">
        <p className="vk-invocation" lang="sa">॥ श्रीमते नारायणाय नमः ॥</p>
        {/* key: a new verse mounts fresh, so its lines rise in again */}
        <figure key={verse} aria-live="polite">
          <blockquote className="vk-sloka" lang="sa">
            {v.padas.map((p, i) => <span key={i} style={{ "--i": i } as React.CSSProperties}>{p}</span>)}
          </blockquote>
          <p className="vk-iast" lang="sa-Latn">{v.iast[0]}<br />{v.iast[1]}</p>
          <figcaption>
            <p className="vk-meaning">{v.meaning}</p>
            <cite>{v.cite}</cite>
          </figcaption>
        </figure>
        {/* each verse's bar fills while it is shown and moves on when full; hovering the side holds it (styles.css) */}
        <nav className="vk-bars" aria-label="Verses">
          {VERSES.map((x, i) => (
            <button key={x.cite} type="button" aria-current={i === verse} onClick={() => setVerse(i)}
              onAnimationEnd={(e) => { if (e.target === e.currentTarget && i === verse) setVerse((i + 1) % VERSES.length); }}>
              {x.short}
            </button>
          ))}
        </nav>
      </aside>}
    </main>
  );
}
