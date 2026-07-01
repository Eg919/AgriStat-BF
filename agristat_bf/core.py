from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ProductionRecord:
    region: str
    cereal: str
    production_tonnes: float
    cultivated_area_hectares: float
    year: int

    def __post_init__(self) -> None:
        if not self.region.strip():
            raise ValueError("region must not be empty")
        if not self.cereal.strip():
            raise ValueError("cereal must not be empty")
        if self.production_tonnes < 0:
            raise ValueError("production_tonnes must be non-negative")
        if self.cultivated_area_hectares <= 0:
            raise ValueError("cultivated_area_hectares must be positive")

    @property
    def yield_per_hectare(self) -> float:
        return self.production_tonnes / self.cultivated_area_hectares


class AgriStatBF:
    def __init__(self, records: Iterable[ProductionRecord] | None = None) -> None:
        self._records: list[ProductionRecord] = list(records or [])

    @property
    def records(self) -> tuple[ProductionRecord, ...]:
        return tuple(self._records)

    def add_record(self, record: ProductionRecord) -> None:
        self._records.append(record)

    def _filtered_records(self, year: int | None = None) -> list[ProductionRecord]:
        if year is None:
            return list(self._records)
        return [record for record in self._records if record.year == year]

    def total_production_by_region(self, year: int | None = None) -> dict[str, float]:
        totals: dict[str, float] = {}
        for record in self._filtered_records(year):
            totals[record.region] = totals.get(record.region, 0.0) + record.production_tonnes
        return dict(sorted(totals.items()))

    def average_yield_by_cereal(self, year: int | None = None) -> dict[str, float]:
        grouped: dict[str, list[float]] = {}
        for record in self._filtered_records(year):
            grouped.setdefault(record.cereal, []).append(record.yield_per_hectare)
        return {
            cereal: sum(values) / len(values)
            for cereal, values in sorted(grouped.items())
        }

    def top_region_for_cereal(self, cereal: str, year: int | None = None) -> str | None:
        cereal_name = cereal.strip().casefold()
        matching_records = [
            record
            for record in self._filtered_records(year)
            if record.cereal.casefold() == cereal_name
        ]
        if not matching_records:
            return None
        return max(matching_records, key=lambda record: record.production_tonnes).region

    def render_region_production_chart(self, year: int | None = None, width: int = 40) -> str:
        totals = self.total_production_by_region(year)
        if not totals:
            return "Aucune donnée disponible."

        max_value = max(totals.values())
        lines = ["Production céréalière par région"]
        for region, total in totals.items():
            bar_length = max(1, round((total / max_value) * width))
            lines.append(f"{region:20} | {'#' * bar_length} {total:.0f} t")
        return "\n".join(lines)
