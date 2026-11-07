import { useRef, useState } from "react";

const iconPaths = {
  shield: <><path d="M12 3 19 6v5c0 4.7-2.8 8-7 10-4.2-2-7-5.3-7-10V6l7-3Z" /><path d="m9 12 2 2 4-4" /></>,
  upload: <><path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5" /><path d="M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" /></>,
  scan: <><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 4 4M8 11h5m-2.5-2.5v5" /></>,
  file: <><path d="M6 3.8h7l5 5v11.4H6z" /><path d="M13 4v5h5M9 14h6m-6 3h6" /></>,
  eye: <><path d="M2.5 12s3.2-6 9.5-6 9.5 6 9.5 6-3.2 6-9.5 6-9.5-6-9.5-6Z" /><circle cx="12" cy="12" r="2.5" /></>,
  bolt: <path d="m13 2-9 12h7l-1 8 10-13h-7z" />,
  hash: <><path d="M5 9h14M4 15h14M10 3 8 21m8-18-2 18" /></>,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  alert: <><path d="M10.3 4.3 2.8 17.2A1.8 1.8 0 0 0 4.4 20h15.2a1.8 1.8 0 0 0 1.6-2.8L13.7 4.3a2 2 0 0 0-3.4 0Z" /><path d="M12 9v4m0 3h.01" /></>,
  close: <><path d="m18 6-12 12M6 6l12 12" /></>,
};

function Icon({ name, size = 20, className = "" }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {iconPaths[name]}
    </svg>
  );
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function Finding({ finding }) {
  const context = [finding.source, finding.page ? `page ${finding.page}` : null, finding.location]
    .filter(Boolean)
    .join(" · ");

  return (
    <article className="finding">
      <div className="finding-heading">
        <div className="finding-title">
          <span className={`severity-dot ${finding.severity || "info"}`} />
          {String(finding.type || "Suspicious content").replaceAll("_", " ")}
        </div>
        <span className={`severity-label ${finding.severity || "info"}`}>{finding.severity || "info"}</span>
      </div>
      {finding.explanation && <p className="finding-explanation">{finding.explanation}</p>}
      {finding.exact_text && <blockquote>{finding.exact_text}</blockquote>}
      {context && <div className="finding-context">{context}</div>}
    </article>
  );
}

function Report({ report }) {
  const score = Math.max(0, Math.min(100, Number(report.risk_score) || 0));
  const findings = Array.isArray(report.findings) ? report.findings : [];
  const approved = report.decision === "approved";

  return (
    <section className="report-card" aria-live="polite">
      <div className="report-topline">
        <div>
          <div className="section-kicker">Scan results</div>
          <h2>Document report</h2>
        </div>
        <span className={`decision-badge ${approved ? "approved" : "quarantined"}`}>
          <span className="badge-dot" />{approved ? "Approved" : "Quarantined"}
        </span>
      </div>

      <div className="report-file">
        <span className="report-file-icon"><Icon name="file" size={18} /></span>
        <span className="report-file-name">{report.filename}</span>
        <span className="report-file-type">{String(report.file_type || "").toUpperCase()}</span>
      </div>

      <div className="report-summary">
        <div className="score-gauge" style={{ "--score": `${score}%`, "--gauge-color": approved ? "#159b75" : "#df5963" }}>
          <div className="score-gauge-center">
            <strong>{score}</strong>
            <span>RISK SCORE</span>
          </div>
        </div>
        <div className="summary-copy">
          <div className={`risk-label ${approved ? "safe" : "danger"}`}>{report.risk_level} risk</div>
          <h3>{approved ? "Looks clear at first glance." : "Review recommended."}</h3>
          <p>{approved
            ? "This document scored below the quarantine threshold."
            : "DocTrap found signals that may need a closer look before this document is used."}</p>
        </div>
      </div>

      <div className="metric-grid">
        <div className="metric">
          <span className="metric-icon lavender"><Icon name="eye" size={17} /></span>
          <span className="metric-text"><strong>{findings.length}</strong><small>Signals found</small></span>
        </div>
        <div className="metric">
          <span className="metric-icon mint"><Icon name="clock" size={17} /></span>
          <span className="metric-text"><strong>{report.scan_time_ms ?? "—"}<small className="unit"> ms</small></strong><small>Scan duration</small></span>
        </div>
        <div className="metric">
          <span className="metric-icon blue"><Icon name="hash" size={17} /></span>
          <span className="metric-text"><strong>{report.sha256 ? `${report.sha256.slice(0, 10)}…` : "—"}</strong><small>SHA-256 fingerprint</small></span>
        </div>
      </div>

      <div className="findings-section">
        <div className="findings-header">
          <div><h3>Detected signals</h3><p>Evidence identified during document inspection</p></div>
          <span className="findings-count">{findings.length}</span>
        </div>
        {findings.length ? (
          <div className="findings-list">{findings.map((finding, index) => <Finding key={finding.id || index} finding={finding} />)}</div>
        ) : (
          <div className="empty-report"><span className="empty-check"><Icon name="check" size={18} /></span>No suspicious signals detected.</div>
        )}
      </div>
    </section>
  );
}

export default function App() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState(null);

  function chooseFile(candidate) {
    if (!candidate) return;
    const extension = candidate.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx"].includes(extension)) {
      setError("Choose a PDF or DOCX file to scan.");
      return;
    }
    if (candidate.size > 20 * 1024 * 1024) {
      setError("This file is larger than the 20 MB upload limit.");
      return;
    }
    setFile(candidate);
    setError("");
    setReport(null);
  }

  async function scanDocument(event) {
    event.preventDefault();
    if (!file || loading) return;
    setLoading(true);
    setError("");
    setReport(null);
    const body = new FormData();
    body.append("file", file);

    try {
      const response = await fetch("/upload", { method: "POST", body });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "The document could not be scanned.");
      setReport(payload);
      requestAnimationFrame(() => document.getElementById("scan-report")?.scrollIntoView({ behavior: "smooth", block: "start" }));
    } catch (scanError) {
      setError(scanError.message || "Unable to connect to DocTrap. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function removeFile(event) {
    event.stopPropagation();
    setFile(null);
    setError("");
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/" aria-label="DocTrap home">
          <span className="brand-symbol"><Icon name="shield" size={21} /></span>
          <span>DocTrap<span className="brand-period">.</span></span>
        </a>
        <div className="workspace-switcher">
          <span className="workspace-avatar">D</span>
          <span className="workspace-copy"><strong>Default workspace</strong><small>Security workspace</small></span>
          <span className="workspace-chevron">⌄</span>
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav className="sidebar-nav" aria-label="Workspace navigation">
          <a className="nav-item active" href="#scanner"><Icon name="scan" size={17} /><span>Document scanner</span><span className="active-indicator" /></a>
          <a className="nav-item" href="#protection"><Icon name="shield" size={17} /><span>Protection checks</span></a>
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-secure-icon"><Icon name="shield" size={17} /></div>
          <strong>Private by design</strong>
          <p>Documents are processed by your DocTrap server.</p>
          <span className="server-status"><i />LOCAL SCANNER</span>
        </div>
        <div className="sidebar-version">DOCTRAP <span>·</span> DOCUMENT SECURITY</div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div className="topbar-breadcrumb"><span>Workspace</span><b>/</b><strong>Document scanner</strong></div>
          <div className="header-right">
            <span className="system-status"><span />Scanner ready</span>
            <span className="header-divider" />
            <span className="header-caption">Secure workspace</span>
            <span className="user-avatar">DS</span>
          </div>
        </header>
        <main className="main-content">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><span className="eyebrow-line" />DOCUMENT SECURITY</div>
            <h1>Inspect documents.<br /><span>Protect your AI.</span></h1>
            <p>Identify hidden content, invisible characters, and suspicious instructions before documents enter your AI workflows.</p>
          </div>
          <div className="inspection-panel">
            <div className="inspection-panel-heading"><span className="inspection-emblem"><Icon name="shield" size={18} /></span><span>INSPECTION PIPELINE</span><span className="pipeline-live"><i />ACTIVE</span></div>
            <div className="pipeline-step"><span className="pipeline-number">01</span><span><strong>Document structure</strong><small>PDF &amp; DOCX analysis</small></span><Icon name="check" size={15} /></div>
            <div className="pipeline-step"><span className="pipeline-number">02</span><span><strong>Content signals</strong><small>Rules &amp; pattern detection</small></span><Icon name="check" size={15} /></div>
            <div className="pipeline-step"><span className="pipeline-number">03</span><span><strong>Risk assessment</strong><small>Explainable scan report</small></span><Icon name="check" size={15} /></div>
            </div>
        </section>

        <div className="section-heading" id="scanner"><div><span className="section-overline">SECURITY WORKSPACE</span><h2>Start a new scan</h2><p>Upload a document for a detailed security inspection.</p></div><span className="supported-formats"><Icon name="file" size={15} /> PDF <i /> DOCX</span></div>
        <div className="workspace-grid">
          <section className="scanner-card">
            <div className="card-title-row">
              <div className="card-title-copy"><span className="step-label">UPLOAD DOCUMENT</span><h2>Choose a file to inspect</h2><p>Drag and drop your document, or select it from your device.</p></div>
              <div className="card-title-icon"><Icon name="upload" size={19} /></div>
            </div>

            <form onSubmit={scanDocument}>
              <input ref={inputRef} className="visually-hidden" type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={event => chooseFile(event.target.files?.[0])} />
              <div
                className={`drop-area ${dragging ? "drag-active" : ""} ${file ? "has-file" : ""}`}
                onClick={() => inputRef.current?.click()}
                onKeyDown={event => {
                  if (event.target !== event.currentTarget) return;
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    inputRef.current?.click();
                  }
                }}
                onDragOver={event => { event.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={event => {
                  event.preventDefault();
                  setDragging(false);
                  chooseFile(event.dataTransfer.files?.[0]);
                }}
                role="button"
                tabIndex={0}
                aria-label="Choose or drop a PDF or DOCX file"
              >
                {file ? (
                  <div className="selected-document">
                    <div className={`document-type ${file.name.toLowerCase().endsWith(".docx") ? "word" : ""}`}>
                      {file.name.toLowerCase().endsWith(".docx") ? "DOC" : "PDF"}
                    </div>
                    <div className="selected-document-copy"><strong>{file.name}</strong><span>{formatBytes(file.size)} <i /> Ready to scan</span></div>
                    <button className="remove-document" type="button" aria-label="Remove file" onClick={removeFile}><Icon name="close" size={17} /></button>
                  </div>
                ) : (
                  <div className="drop-empty">
                    <span className="upload-symbol"><Icon name="upload" size={23} /></span>
                    <strong>Drop your file here</strong>
                    <span className="drop-or">or <span>browse files</span></span>
                  </div>
                )}
                <div className="drop-meta"><span>PDF or DOCX</span><i /><span>Maximum 20 MB</span></div>
              </div>

              {error && <div className="error-message" role="alert"><Icon name="alert" size={17} />{error}</div>}
              <button className="scan-button" type="submit" disabled={!file || loading}>
                {loading ? <><span className="spinner" />Inspecting document…</> : <><Icon name="scan" size={18} />Scan document<span className="button-arrow">→</span></>}
              </button>
            </form>

            <div className="secure-note"><Icon name="shield" size={15} /><span>Your file is checked by the DocTrap server and not sent to third-party services.</span></div>
          </section>

          <aside className="info-column" id="protection">
            <section className="checks-card">
              <div className="checks-title"><span className="checks-icon"><Icon name="eye" size={17} /></span><div><h2>What we look for</h2><p>Signals that can hide in plain sight.</p></div></div>
              <div className="check-item"><span className="check-icon"><Icon name="eye" size={16} /></span><div><strong>Hidden content</strong><span>Unusual text and document metadata</span></div></div>
              <div className="check-item"><span className="check-icon"><Icon name="bolt" size={16} /></span><div><strong>Prompt injection</strong><span>Instructions aimed at AI systems</span></div></div>
              <div className="check-item"><span className="check-icon"><Icon name="hash" size={16} /></span><div><strong>Invisible characters</strong><span>Unicode tricks and hidden text</span></div></div>
            </section>
            <section className="threshold-card">
              <div className="threshold-top"><span className="threshold-icon"><Icon name="shield" size={17} /></span><span>RISK THRESHOLD</span></div>
              <div className="threshold-value">25<span> / 100</span></div>
              <p>Documents scoring 25 or higher are flagged for review.</p>
              <div className="threshold-meter"><span /></div>
              <div className="threshold-labels"><span>Low risk</span><span>Review</span></div>
            </section>
          </aside>
        </div>

        {report && <div id="scan-report"><Report report={report} /></div>}

        <footer className="page-footer"><span>DOCTRAP DOCUMENT SECURITY</span><span>Inspect · Understand · Decide</span></footer>
        </main>
      </div>
    </div>
  );
}
