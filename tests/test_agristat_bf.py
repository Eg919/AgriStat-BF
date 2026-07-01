import unittest

from agristat_bf import AgriStatBF, ProductionRecord


class AgriStatBFTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = AgriStatBF(
            [
                ProductionRecord("Boucle du Mouhoun", "Maïs", 1200, 400, 2024),
                ProductionRecord("Boucle du Mouhoun", "Mil", 600, 300, 2024),
                ProductionRecord("Hauts-Bassins", "Maïs", 1500, 500, 2024),
                ProductionRecord("Centre", "Sorgho", 700, 350, 2023),
            ]
        )

    def test_centralizes_and_aggregates_production_by_region(self) -> None:
        self.assertEqual(
            self.tool.total_production_by_region(2024),
            {
                "Boucle du Mouhoun": 1800.0,
                "Hauts-Bassins": 1500.0,
            },
        )

    def test_computes_decision_support_indicators(self) -> None:
        self.assertEqual(self.tool.top_region_for_cereal("maïs", 2024), "Hauts-Bassins")
        self.assertIsNone(self.tool.top_region_for_cereal("Riz", 2024))
        self.assertEqual(
            self.tool.average_yield_by_cereal(2024),
            {"Maïs": 3.0, "Mil": 2.0},
        )

    def test_renders_textual_visualization(self) -> None:
        chart = self.tool.render_region_production_chart(2024, width=10)

        self.assertIn("Production céréalière par région", chart)
        self.assertIn("Boucle du Mouhoun", chart)
        self.assertIn("########## 1800 t", chart)

    def test_rejects_invalid_record_values(self) -> None:
        with self.assertRaises(ValueError):
            ProductionRecord("", "Maïs", 100, 20, 2024)

        with self.assertRaises(ValueError):
            ProductionRecord("Centre", "Maïs", -1, 20, 2024)


if __name__ == "__main__":
    unittest.main()
