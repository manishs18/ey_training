import { mealField } from '../utils/meal'

export default function HistoryPage({ selectedDate, setSelectedDate, history, loadHistory }) {
  const filtered = history.filter((meal) => {
    const time = meal.meal_time || meal.created_at
    return !selectedDate || (time && new Date(time).toISOString().slice(0, 10) === selectedDate)
  })

  return (
    <section className="panel page-panel">
      <div className="report-head">
        <h2>Meal History</h2>
        <button onClick={loadHistory}>Refresh</button>
      </div>
      <div className="date-row">
        <label>
          History date
          <input type="date" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} />
        </label>
      </div>
      <div className="history">
        {filtered.length === 0 && <p className="muted">No meals for this date.</p>}
        {filtered.map((meal) => (
          <article key={meal.id}>
            <strong>#{meal.id} {meal.meal_type || 'meal'}</strong>
            <span className={`status ${meal.status?.toLowerCase()}`}>{meal.status}</span>
            <p>{meal.meal_time ? new Date(meal.meal_time).toLocaleString() : 'No time set'}</p>
            <p><b>Foods:</b> {mealField(meal, 'foods_text', 'Foods')}</p>
            <p><b>Drinks:</b> {mealField(meal, 'drinks_text', 'Drinks')}</p>
            <p><b>Supplements:</b> {mealField(meal, 'supplements_text', 'Supplements/medicine')}</p>
            <p><b>Notes:</b> {mealField(meal, 'notes_text', 'Notes')}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
