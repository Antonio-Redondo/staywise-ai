import { test, expect } from '@playwright/test'

test('recommendation flow renders and submits query', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Find homes you\'ll love')).toBeVisible()

  const textarea = page.getByLabel('Describe what you want')
  await textarea.fill('2 bedroom apartment near BART under $1,200,000')
  await page.getByRole('button', { name: /find recommendations/i }).click()

  await expect(page.getByText(/Results|Intent|Neighborhoods|Listings/)).toBeVisible()
})
