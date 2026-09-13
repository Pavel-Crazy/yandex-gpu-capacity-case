"""
Кейс 1 — оценка вычислительной мощности OpenAI и Anthropic
Дата оценки: 13.09.2026

Цель:
1) привести неоднородные парки ускорителей к H100-эквивалентам (H100e);
2) обновить системную оценку Epoch AI на конец 2025 до сентября 2026;
3) показать сценарный диапазон;
4) отдельно задать диапазон распределения между инференсом и обучением/исследованиями.

Важно:
- это аналитическая оценка, а не официальное раскрытие компаний;
- базовый расчёт исключает будущую/законтрактованную мощность;
- верхний сценарий Anthropic содержит неподтверждённую добавку 200 000 H100e;
- проценты для общих площадок — допущения модели.
"""

AS_OF = "2026-09-13"

# -----------------------------
# OpenAI
# -----------------------------
OPENAI_BASE_2025 = 1_743_000  # H100e, Epoch AI, конец 2025

openai_sites = [
    # name, h100e_end_2025, h100e_current, attribution_low, attribution_base, attribution_high
    ("Stargate Abilene",      255_000, 509_000, 1.00, 1.00, 1.00),
    ("CoreWeave Denton",       65_000, 253_000, 0.70, 0.80, 1.00),
    ("Fairwater Atlanta",     388_000, 769_000, 0.50, 0.65, 1.00),
    ("Fairwater Wisconsin",         0, 446_000, 0.50, 0.65, 1.00),
]

def scenario_total(baseline, rows, scenario_index):
    total = baseline
    detail = []
    for row in rows:
        name, old, current, low, base, high = row
        share = (low, base, high)[scenario_index]
        increment = current - old
        attributed = increment * share
        total += attributed
        detail.append((name, increment, share, attributed))
    return total, detail

openai_low, openai_low_detail = scenario_total(OPENAI_BASE_2025, openai_sites, 0)
openai_base, openai_base_detail = scenario_total(OPENAI_BASE_2025, openai_sites, 1)
openai_high, openai_high_detail = scenario_total(OPENAI_BASE_2025, openai_sites, 2)

# -----------------------------
# Anthropic
# -----------------------------
ANTHROPIC_BASE_2025 = 1_190_000  # H100e, Epoch AI, конец 2025

# Rainier / New Carlisle: 471k -> 686k
rainier_increment = 686_000 - 471_000

# Colossus 1: 276k H100e, весь центр доступен Anthropic
colossus1_h100e = 276_000

# SEC: ~325k NVIDIA GPU across Colossus 1 + Colossus 2.
# Epoch: Colossus 1 = ~230k physical GPU, значит ~95k GPU относятся к Colossus 2.
anthropic_colossus2_gpu = 325_000 - 230_000

# Epoch: Colossus 2 ≈1.112M H100e на 440k B200/B300
colossus2_h100e_per_gpu = 1_112_000 / 440_000
colossus2_base_h100e = anthropic_colossus2_gpu * colossus2_h100e_per_gpu

# Lake Mariner: 59k H100e, Anthropic — вероятный пользователь
lake_mariner_h100e = 59_000

# Сценарии:
# low: Colossus2 85% от базовой оценки, Lake Mariner 50%
# base: Colossus2 100%, Lake Mariner 80%
# high: Colossus2 115%, Lake Mariner 100% + 200k H100e возможного доп. 2026 compute
anthropic_low = (
    ANTHROPIC_BASE_2025
    + rainier_increment
    + colossus1_h100e
    + colossus2_base_h100e * 0.85
    + lake_mariner_h100e * 0.50
)
anthropic_base = (
    ANTHROPIC_BASE_2025
    + rainier_increment
    + colossus1_h100e
    + colossus2_base_h100e
    + lake_mariner_h100e * 0.80
)
anthropic_high = (
    ANTHROPIC_BASE_2025
    + rainier_increment
    + colossus1_h100e
    + colossus2_base_h100e * 1.15
    + lake_mariner_h100e
    + 200_000
)

# -----------------------------
# Распределение нагрузки
# -----------------------------
# Публичного точного текущего split нет.
INFERENCE_LOW = 0.45
INFERENCE_BASE = 0.50
INFERENCE_HIGH = 0.55

def fmt_m(x):
    return f"{x/1_000_000:.2f} млн H100e"

print(f"Дата оценки: {AS_OF}")
print()
print("OpenAI:")
print("  low :", fmt_m(openai_low))
print("  base:", fmt_m(openai_base))
print("  high:", fmt_m(openai_high))
print()
print("Anthropic:")
print("  low :", fmt_m(anthropic_low))
print("  base:", fmt_m(anthropic_base))
print("  high:", fmt_m(anthropic_high))
print()
print("Центральная оценка распределения:")
print(f"  инференс: {INFERENCE_BASE:.0%}")
print(f"  обучение и исследования: {1-INFERENCE_BASE:.0%}")
print(f"  разумный диапазон инференса: {INFERENCE_LOW:.0%}–{INFERENCE_HIGH:.0%}")

# Числа, используемые на слайде:
print()
print("Округление для слайда:")
print(f"  OpenAI ≈ {openai_base/1_000_000:.1f} млн H100e")
print(f"  Anthropic ≈ {anthropic_base/1_000_000:.1f} млн H100e")
