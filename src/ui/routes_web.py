from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/ui", response_class=HTMLResponse, summary="Веб-форма для расчётов InvestCalc", tags=["web"])
async def investcalc_form() -> str:
    """Простая HTML-страница с формой для расчёта TCO/ROI/Payback."""
    ## Всё в одном HTML (для учебного проекта этого достаточно)
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8" />
    <title>InvestCalc — Веб-форма расчёта</title>
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            padding: 20px;
            background: ##f5f5f7;
        }
        h1 {
            margin-bottom: 0.2rem;
        }
        .subtitle {
            margin-top: 0;
            color: ##555;
            font-size: 0.95rem;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: ##fff;
            border-radius: 12px;
            padding: 20px 24px 24px;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px 24px;
            margin-top: 16px;
        }
        label {
            display: block;
            font-size: 0.9rem;
            margin-bottom: 4px;
            color: ##333;
        }
        input[type="text"],
        input[type="number"] {
            width: 100%;
            box-sizing: border-box;
            padding: 6px 8px;
            border-radius: 6px;
            border: 1px solid ##ccc;
            font-size: 0.9rem;
        }
        input[type="number"]::-webkit-outer-spin-button,
        input[type="number"]::-webkit-inner-spin-button {
            margin: 0;
        }
        .actions {
            margin-top: 18px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        button {
            padding: 8px 16px;
            border-radius: 999px;
            border: none;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            background: ##2563eb;
            color: ##fff;
        }
        button.secondary {
            background: ##e5e7eb;
            color: ##111827;
        }
        button:disabled {
            opacity: 0.6;
            cursor: default;
        }
        ##status {
            font-size: 0.85rem;
            color: ##555;
        }
        .result {
            margin-top: 20px;
            padding: 12px 14px;
            border-radius: 8px;
            background: ##f3f4ff;
            font-family: "JetBrains Mono", "Fira Code", monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
        }
        .result h2 {
            margin: 0 0 8px;
            font-size: 1rem;
        }
        .note {
            margin-top: 12px;
            font-size: 0.8rem;
            color: ##6b7280;
        }
        @media (max-width: 720px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>InvestCalc — Расчёт эффективности ИС</h1>
    <p class="subtitle">
        Введите исходные данные (CAPEX, OPEX, эффекты, период) и нажмите
        <strong>«Рассчитать»</strong>. Форма отправит запрос в API <code>/api/v1/calc</code>.
    </p>

    <div class="grid">
        <div>
            <label for="project_name">Название проекта</label>
            <input id="project_name" type="text" value="CRM локально" />
        </div>

        <div>
            <label for="capex">CAPEX (капитальные затраты)</label>
            <input id="capex" type="number" value="150000" step="1000" />
        </div>

        <div>
            <label for="opex">OPEX (операционные затраты в периоде)</label>
            <input id="opex" type="number" value="30000" step="1000" />
        </div>

        <div>
            <label for="effects">Effects (экономический эффект)</label>
            <input id="effects" type="number" value="180000" step="1000" />
        </div>

        <div>
            <label for="period_months">Период анализа, месяцев</label>
            <input id="period_months" type="number" value="36" step="1" />
        </div>

        <div>
            <label for="discount_rate_percent">Ставка дисконтирования, % (опционально)</label>
            <input id="discount_rate_percent" type="number" step="0.1" placeholder="оставьте пустым, если не нужно" />
        </div>
    </div>

    <div class="actions">
        <button id="calcBtn">Рассчитать</button>
        <button id="resetBtn" class="secondary">Сбросить</button>
        <span id="status"></span>
    </div>

    <div class="result" id="resultBox" style="display: none;">
        <h2>Результат расчёта</h2>
        <div id="resultText"></div>
    </div>

    <p class="note">
        ⚙ Формат запроса соответствует модели <code>InvestInput</code>.<br />
        Вы можете открыть <code>/docs</code> и посмотреть тот же запрос в Swagger UI.
    </p>
</div>

<script>
    const statusEl = document.getElementById("status");
    const resultBox = document.getElementById("resultBox");
    const resultText = document.getElementById("resultText");
    const calcBtn = document.getElementById("calcBtn");
    const resetBtn = document.getElementById("resetBtn");

    function setStatus(msg) {
        statusEl.textContent = msg || "";
    }

    function getPayload() {
        const project_name = document.getElementById("project_name").value.trim();
        const capex = Number(document.getElementById("capex").value);
        const opex = Number(document.getElementById("opex").value);
        const effects = Number(document.getElementById("effects").value);
        const period_months = Number(document.getElementById("period_months").value);
        const discountStr = document.getElementById("discount_rate_percent").value;
        const discount_rate_percent = discountStr === "" ? null : Number(discountStr);

        return {
            project_name,
            capex,
            opex,
            effects,
            period_months,
            discount_rate_percent
        };
    }

    async function callApi() {
        try {
            const payload = getPayload();

            if (!payload.project_name) {
                alert("Заполните название проекта");
                return;
            }

            calcBtn.disabled = true;
            setStatus("Отправка запроса в /api/v1/calc ...");

            const resp = await fetch("/api/v1/calc", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!resp.ok) {
                const text = await resp.text();
                throw new Error("Ошибка API: " + resp.status + " " + text);
            }

            const data = await resp.json();

            resultBox.style.display = "block";
            resultText.innerHTML =
                "Проект: <strong>" + (data.project_name || payload.project_name) + "</strong><br>" +
                "TCO: <strong>" + (data.tco ?? "—") + "</strong><br>" +
                "ROI, %: <strong>" + (data.roi_percent ?? data.roi ?? "—") + "</strong><br>" +
                "Срок окупаемости (мес.): <strong>" + (data.payback_months ?? "—") + "</strong><br>" +
                "Срок окупаемости (лет): <strong>" + (data.payback_years ?? "—") + "</strong><br>" +
                (data.note ? ("Комментарий: " + data.note) : "");

            setStatus("Расчёт выполнен успешно.");
        } catch (err) {
            console.error(err);
            resultBox.style.display = "block";
            resultText.textContent = "Ошибка: " + err.message;
            setStatus("Произошла ошибка при расчёте.");
        } finally {
            calcBtn.disabled = false;
        }
    }

    calcBtn.addEventListener("click", () => {
        callApi();
    });

    resetBtn.addEventListener("click", () => {
        document.getElementById("project_name").value = "CRM локально";
        document.getElementById("capex").value = "150000";
        document.getElementById("opex").value = "30000";
        document.getElementById("effects").value = "180000";
        document.getElementById("period_months").value = "36";
        document.getElementById("discount_rate_percent").value = "";
        resultBox.style.display = "none";
        resultText.textContent = "";
        setStatus("");
    });
</script>

</body>
</html>
    """
