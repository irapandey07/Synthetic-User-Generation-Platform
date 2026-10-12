import { useState } from "react";

const DEFAULTS = {
  productDescription: "",
  targetAudience: "",
  researchObjective: "",
  count: 4,
};

export default function ResearchForm({ onGenerate, isLoading }) {
  const [form, setForm] = useState(DEFAULTS);

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    onGenerate(form);
  }

  return (
    <form className="intake-card" onSubmit={handleSubmit}>
      <p className="intake-label">Milestone 1 · Develop — Survey Mode</p>
      <h2>Research brief</h2>

      <div className="field">
        <label htmlFor="productDescription">Product description</label>
        <textarea
          id="productDescription"
          rows={3}
          placeholder="e.g. a refillable, fragrance-free bar soap subscription"
          value={form.productDescription}
          onChange={(e) => update("productDescription", e.target.value)}
          required
        />
      </div>

      <div className="field">
        <label htmlFor="targetAudience">Target audience</label>
        <textarea
          id="targetAudience"
          rows={2}
          placeholder="e.g. ages 50-60, active-duty and retired military"
          value={form.targetAudience}
          onChange={(e) => update("targetAudience", e.target.value)}
          required
        />
      </div>

      <div className="field">
        <label htmlFor="researchObjective">Research objective</label>
        <textarea
          id="researchObjective"
          rows={2}
          placeholder="e.g. how many people prefer a different soap, and why"
          value={form.researchObjective}
          onChange={(e) => update("researchObjective", e.target.value)}
          required
        />
      </div>

      <div className="field-row">
        <div className="field" style={{ marginBottom: 0 }}>
          <label htmlFor="count">Personas to generate</label>
          <input
            id="count"
            type="number"
            min={1}
            max={100}
            value={form.count}
            onChange={(e) => update("count", e.target.value)}
          />
        </div>
      </div>

      <button className="generate-btn" type="submit" disabled={isLoading}>
        {isLoading ? "Generating…" : "Generate personas"}
      </button>
    </form>
  );
}
