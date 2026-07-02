const mealTypeOrder = ['breakfast', 'lunch', 'dinner', 'snack']

const mealTypeLabel = (value) => {
  if (!value) return 'Meal'
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export function buildMealCoverage(meals = []) {
  const loggedTypes = new Set(
    (meals || [])
      .map((meal) => (meal?.meal_type || '').toLowerCase())
      .filter(Boolean)
  )

  const items = mealTypeOrder.map((type) => ({
    key: type,
    label: mealTypeLabel(type),
    status: loggedTypes.has(type) ? 'logged' : 'missed',
    note: loggedTypes.has(type) ? 'Logged for today' : 'Plan to add this meal',
  }))

  const missedMeals = items.filter((item) => item.status === 'missed').map((item) => item.key)

  return {
    items,
    missedMeals,
    coveragePercent: Math.round((items.filter((item) => item.status === 'logged').length / items.length) * 100),
  }
}

export function buildDashboardInsight(profile = {}, meals = [], reportSummary = '') {
  const combinedText = [reportSummary, ...meals.map((meal) => `${meal?.meal_type || ''} ${meal?.meal_text || ''}`).filter(Boolean)].join(' ').toLowerCase()
  const goodHabits = []
  const needsAttention = []
  const dietPlan = []

  if (meals.some((meal) => /paneer|curd|egg|eggs|dal|chana|tofu|soy|fish|chicken/.test(`${meal?.meal_text || ''}`.toLowerCase()))) {
    goodHabits.push('Protein-rich foods were logged at least once today.')
  }

  if (/water|hydration|juice/.test(combinedText)) {
    goodHabits.push('Hydration cues were included in the day log.')
  }

  if (!meals.length) {
    needsAttention.push('No meal entries were found for this date yet.')
  }

  if (/tea|coffee|chai/.test(combinedText) && /iron/.test((profile?.health_conditions_text || '').toLowerCase() + ' ' + (profile?.deficiencies_text || '').toLowerCase())) {
    needsAttention.push('Tea or coffee was logged, which may need a wider gap from iron-rich meals or supplements.')
  }

  const coverage = buildMealCoverage(meals)
  if (coverage.missedMeals.length) {
    needsAttention.push(`Missing ${coverage.missedMeals.join(', ')} logging for a more complete day.`)
  }

  if (/low protein|protein/.test(combinedText) || !meals.some((meal) => /paneer|curd|egg|eggs|dal|chana|tofu|soy|fish|chicken/.test(`${meal?.meal_text || ''}`.toLowerCase()))) {
    needsAttention.push('Protein intake looks light; add a protein anchor to breakfast or lunch.')
  }

  const goal = (profile?.goal || profile?.goals?.[0] || 'balanced eating').toString().replace(/_/g, ' ')
  const dietType = (profile?.diet_type || 'balanced').toString().replace(/_/g, ' ')
  const gender = profile?.gender || 'your profile'
  const age = profile?.age || 'your age'
  const weight = profile?.weight_kg || 'your weight'

  dietPlan.push(`Keep ${goal} as the main theme and structure the day around 3 balanced meals.`)
  dietPlan.push(`Use a ${dietType} pattern with a protein-rich breakfast, a fiber-rich lunch, and a lighter dinner if needed.`)
  dietPlan.push(`For ${gender}, ${age}, and ${weight} kg, aim for steady meals and protein at each meal rather than one big intake.`)

  return {
    goodHabits,
    needsAttention,
    dietPlan,
    profileSummary: [
      goal && `Goal: ${goal}`,
      dietType && `Diet: ${dietType}`,
      gender && `Gender: ${gender}`,
      age && `Age: ${age}`,
      weight && `Weight: ${weight} kg`,
    ].filter(Boolean),
  }
}
