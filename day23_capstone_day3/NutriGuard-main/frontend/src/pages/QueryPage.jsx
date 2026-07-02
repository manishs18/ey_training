export default function QueryPage({ queryText, setQueryText, submitNutritionQuery, queryResponse, queryLoading }) {
  return (
    <section className="panel page-panel">
      <h2>Nutrition Query</h2>
      <p>Ask for personalized guidance based on your body metrics, goals, and logged meals.</p>
      <label>
        Ask your nutrition question
        <textarea
          value={queryText}
          onChange={(event) => setQueryText(event.target.value)}
          rows={4}
        />
      </label>
      <button onClick={submitNutritionQuery} disabled={queryLoading || !queryText.trim()}>
        {queryLoading ? 'Thinking ...' : 'Ask the AI'}
      </button>
      {queryResponse && (
        <div className="parsed-box">
          <h3>AI Response</h3>
          <pre>{queryResponse}</pre>
        </div>
      )}
    </section>
  )
}
