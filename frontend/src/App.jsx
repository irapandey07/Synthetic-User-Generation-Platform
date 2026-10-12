import { useState } from "react";
import ResearchForm from "./components/ResearchForm.jsx";
import PersonaCard from "./components/PersonaCard.jsx";
import SurveyResults from "./components/SurveyResults.jsx";
import InterviewResults from "./components/InterviewResults.jsx";
import InterviewChat from "./components/InterviewChat.jsx";
import InsightsPanel from "./components/InsightsPanel.jsx";
import AdoptionScore from "./components/AdoptionScore.jsx";
import Dashboard from "./components/Dashboard.jsx";

export default function App() {
  const [personas, setPersonas] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastBrief, setLastBrief] = useState(null);
  const [surveyResults, setSurveyResults] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [surveyError, setSurveyError] = useState(null);
  const [interviewResults, setInterviewResults] = useState(null);
  const [isInterviewing, setIsInterviewing] = useState(false);
  const [interviewError, setInterviewError] = useState(null);
  const [insights, setInsights] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [insightsError, setInsightsError] = useState(null);
  const [adoptionResult, setAdoptionResult] = useState(null);
  const [isScoring, setIsScoring] = useState(false);
  const [scoringError, setScoringError] = useState(null);
  const [surveyQuestionsText, setSurveyQuestionsText] = useState("");
  const [interviewQuestionsText, setInterviewQuestionsText] = useState("");
  const [isDownloadingReport, setIsDownloadingReport] = useState(false);
  const [reportError, setReportError] = useState(null);

  function linesToQuestions(text) {
    return text
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);
  }

  async function handleGenerate(form) {
    setIsLoading(true);
    setError(null);
    setSurveyResults(null);
    setInterviewResults(null);
    setInsights(null);
    setAdoptionResult(null);
    try {
      const res = await fetch("/api/generate-personas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to generate personas.");
      }
      setPersonas(data.personas || []);
      setLastBrief(form);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSimulateSurvey() {
    if (!lastBrief || personas.length === 0) return;
    setIsSimulating(true);
    setSurveyError(null);
    try {
      const res = await fetch("/api/simulate-survey", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          personas,
          productDescription: lastBrief.productDescription,
          targetAudience: lastBrief.targetAudience,
          researchObjective: lastBrief.researchObjective,
          questions: linesToQuestions(surveyQuestionsText),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to simulate survey.");
      }
      setSurveyResults(data);
    } catch (err) {
      setSurveyError(err.message);
    } finally {
      setIsSimulating(false);
    }
  }

  async function handleSimulateInterview() {
    if (!lastBrief || personas.length === 0) return;
    setIsInterviewing(true);
    setInterviewError(null);
    try {
      const res = await fetch("/api/simulate-interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          personas,
          productDescription: lastBrief.productDescription,
          targetAudience: lastBrief.targetAudience,
          researchObjective: lastBrief.researchObjective,
          questions: linesToQuestions(interviewQuestionsText),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to simulate interview.");
      }
      setInterviewResults(data);
    } catch (err) {
      setInterviewError(err.message);
    } finally {
      setIsInterviewing(false);
    }
  }

  async function handleExtractInsights() {
    if (!lastBrief || personas.length === 0) return;
    setIsExtracting(true);
    setInsightsError(null);
    try {
      const res = await fetch("/api/extract-insights", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          personas,
          surveyResults,
          interviewResults,
          productDescription: lastBrief.productDescription,
          researchObjective: lastBrief.researchObjective,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to extract insights.");
      }
      setInsights(data);
    } catch (err) {
      setInsightsError(err.message);
    } finally {
      setIsExtracting(false);
    }
  }

  async function handleScoreAdoption() {
    if (!lastBrief || personas.length === 0) return;
    setIsScoring(true);
    setScoringError(null);
    try {
      const res = await fetch("/api/score-adoption", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          personas,
          productDescription: lastBrief.productDescription,
          targetAudience: lastBrief.targetAudience,
          researchObjective: lastBrief.researchObjective,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to score adoption.");
      }
      setAdoptionResult(data);
    } catch (err) {
      setScoringError(err.message);
    } finally {
      setIsScoring(false);
    }
  }

  async function handleDownloadReport() {
    if (!lastBrief || personas.length === 0) return;
    setIsDownloadingReport(true);
    setReportError(null);
    try {
      const res = await fetch("/api/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          personas,
          productDescription: lastBrief.productDescription,
          targetAudience: lastBrief.targetAudience,
          researchObjective: lastBrief.researchObjective,
          surveyResults,
          interviewResults,
          insights,
          adoptionResult,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Failed to generate report.");
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "research-report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setReportError(err.message);
    } finally {
      setIsDownloadingReport(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="folder-header">
        <div>
          <span className="folder-tab">
            <span className="dot" />
            Persona Generation Agent
          </span>
          <h1>Synthetic User Research — Case File</h1>
        </div>
        <div className="case-meta">
          Milestones 1–4
          <br />
          7 agents on file
        </div>
      </header>

      <div className="workspace">
        <ResearchForm onGenerate={handleGenerate} isLoading={isLoading} />

        <section>
          <div className="results-header">
            <h2>Generated personas</h2>
            <span className="results-count">
              {personas.length > 0 ? `${personas.length} on file` : ""}
            </span>
          </div>

          {isLoading && (
            <div className="loading-row" style={{ marginBottom: 16 }}>
              <span className="spinner" />
              Drafting synthetic personas from the brief…
            </div>
          )}

          {error && <p className="error-note">{error}</p>}

          {!isLoading && personas.length === 0 && !error && (
            <div className="empty-state">
              No personas generated yet. Fill out the research brief and
              click &ldquo;Generate personas&rdquo; to populate this case
              file.
            </div>
          )}

          <div className="persona-grid">
            {personas.map((p) => (
              <PersonaCard key={p.id} persona={p} />
            ))}
          </div>

          {personas.length > 0 && (
            <>
              <div className="field" style={{ marginTop: 20 }}>
                <label htmlFor="surveyQuestions">
                  Survey questions (optional, one per line — leave blank to use the research objective only)
                </label>
                <textarea
                  id="surveyQuestions"
                  rows={3}
                  placeholder={"e.g.\nWould you switch to this product?\nWhat would make you hesitant?"}
                  value={surveyQuestionsText}
                  onChange={(e) => setSurveyQuestionsText(e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="interviewQuestions">
                  Interview questions (optional, one per line — leave blank for default questions)
                </label>
                <textarea
                  id="interviewQuestions"
                  rows={3}
                  placeholder={"e.g.\nWhat's your current routine around this?\nWhat would need to be true for you to try this?"}
                  value={interviewQuestionsText}
                  onChange={(e) => setInterviewQuestionsText(e.target.value)}
                />
              </div>
            </>
          )}

          {personas.length > 0 && (
            <div style={{ marginTop: 8, display: "flex", gap: 10, flexWrap: "wrap" }}>
              <button
                className="generate-btn"
                style={{ width: "auto", padding: "10px 20px" }}
                onClick={handleSimulateSurvey}
                disabled={isSimulating}
              >
                {isSimulating ? "Simulating…" : "Run survey simulation"}
              </button>
              <button
                className="generate-btn"
                style={{
                  width: "auto",
                  padding: "10px 20px",
                  background: "transparent",
                  color: "var(--teal)",
                  border: "1px solid var(--teal)",
                }}
                onClick={handleSimulateInterview}
                disabled={isInterviewing}
              >
                {isInterviewing ? "Interviewing…" : "Run interview simulation"}
              </button>
            </div>
          )}
          {surveyError && <p className="error-note">{surveyError}</p>}
          {interviewError && <p className="error-note">{interviewError}</p>}

          <SurveyResults results={surveyResults} />
          <InterviewResults results={interviewResults} />

          <InterviewChat personas={personas} lastBrief={lastBrief} />

          {personas.length > 0 && (
            <div style={{ marginTop: 20, display: "flex", gap: 10, flexWrap: "wrap" }}>
              <button
                className="generate-btn"
                style={{ width: "auto", padding: "10px 20px" }}
                onClick={handleExtractInsights}
                disabled={isExtracting || (!surveyResults && !interviewResults)}
                title={!surveyResults && !interviewResults ? "Run survey or interview simulation first" : ""}
              >
                {isExtracting ? "Extracting…" : "Extract insights"}
              </button>
              <button
                className="generate-btn"
                style={{
                  width: "auto",
                  padding: "10px 20px",
                  background: "transparent",
                  color: "var(--mustard)",
                  border: "1px solid var(--mustard)",
                }}
                onClick={handleScoreAdoption}
                disabled={isScoring}
              >
                {isScoring ? "Scoring…" : "Score product adoption"}
              </button>
            </div>
          )}
          {insightsError && <p className="error-note">{insightsError}</p>}
          {scoringError && <p className="error-note">{scoringError}</p>}

          <InsightsPanel insights={insights} />
          <AdoptionScore result={adoptionResult} />

          <Dashboard
            personas={personas}
            insights={insights}
            surveyResults={surveyResults}
            adoptionResult={adoptionResult}
          />

          {personas.length > 0 && (
            <div style={{ marginTop: 20 }}>
              <button
                className="generate-btn"
                style={{ width: "auto", padding: "10px 20px" }}
                onClick={handleDownloadReport}
                disabled={isDownloadingReport}
              >
                {isDownloadingReport ? "Building PDF…" : "Download research report (PDF)"}
              </button>
              {reportError && <p className="error-note">{reportError}</p>}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
