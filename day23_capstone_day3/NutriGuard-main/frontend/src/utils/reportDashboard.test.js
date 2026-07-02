import test from 'node:test'
import assert from 'node:assert/strict'
import { buildMealCoverage, buildDashboardInsight } from './reportDashboard.js'

test('buildMealCoverage marks breakfast lunch dinner and missed meals', () => {
  const coverage = buildMealCoverage([
    { meal_type: 'breakfast', meal_text: 'Poha' },
    { meal_type: 'lunch', meal_text: 'Rice and dal' },
  ])

  assert.equal(coverage.breakfast.status, 'logged')
  assert.equal(coverage.lunch.status, 'logged')
  assert.equal(coverage.dinner.status, 'missed')
  assert.deepEqual(coverage.missedMeals, ['dinner'])
})

test('buildDashboardInsight returns good and bad items from profile and meals', () => {
  const insight = buildDashboardInsight(
    { goal: 'fat_loss', diet_type: 'vegetarian', health_conditions_text: 'Iron deficiency' },
    [{ meal_type: 'breakfast', meal_text: 'Paneer and curd' }],
    'You had paneer and curd.'
  )

  assert.ok(insight.goodHabits.some((item) => item.includes('protein')))
  assert.ok(insight.needsAttention.some((item) => item.includes('iron')))
  assert.ok(insight.dietPlan.some((item) => item.includes('breakfast')))
})
