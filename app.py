from flask import Flask, render_template, request, redirect, url_for
from db_config import load_transactions
from mining_core import data_prep, generate_rules, get_recommendations
from service_names import service_names, name_to_code

app = Flask(__name__)

# Load and prepare data
df = load_transactions()
df = data_prep(df)
rules = generate_rules(df)

@app.route("/")
def home():
    return render_template("index.html", services=service_names)

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if request.method == "GET":
        # Redirect GET requests to home page
        return redirect(url_for("home"))
    
    # Handle POST request
    selected_service = request.form.get("service")
    print("🔍 Selected service from UI:", selected_service)
    
    if not selected_service:
        print("⚠️ Warning: No service selected")
        return render_template(
            "index.html",
            services=service_names,
            selected_service=None,
            recommendations=[]
        )
    
    # Map service name to internal service code
    selected_service_code = name_to_code.get(selected_service)
    if not selected_service_code:
        print(f"⚠️ Warning: Could not find code for service: {selected_service}")
        return render_template(
            "index.html",
            services=service_names,
            selected_service=selected_service,
            recommendations=[]
        )
    
    print(f"✅ Mapped to service code: {selected_service_code}")
    recs = get_recommendations(rules, selected_service_code, top_n=3)
    print(f"📊 Found {len(recs)} recommendations")
    
    return render_template(
        "index.html",
        services=service_names,
        selected_service=selected_service,
        recommendations=recs
    )

@app.route("/analytics")
def analytics():
    # Popular services
    service_counts = (
        df['Service']
        .value_counts()
        .head(10)
        .rename_axis('service_code')
        .reset_index(name='count')
    )
    service_counts['service_name'] = service_counts['service_code'].map(service_names)

    # Monthly booking trend
    monthly = (
        df.groupby('New_Date')['Service']
          .count()
          .rename("count")
          .reset_index()
    )

    # Top association rules
    top_rules = (
        rules.sort_values("lift", ascending=False)
             .head(10)
             .copy()
    )
    top_rules['antecedent'] = top_rules['antecedents'].apply(lambda x: service_names.get(list(x)[0], list(x)[0]))
    top_rules['consequent'] = top_rules['consequents'].apply(lambda x: service_names.get(list(x)[0], list(x)[0]))

    return render_template(
        "analytics.html",
        service_counts=service_counts.to_dict(orient="records"),
        monthly=monthly.to_dict(orient="records"),
        top_rules=top_rules[['antecedent', 'consequent', 'support', 'confidence', 'lift']].to_dict(orient="records")
    )

@app.route("/test_all")
def test_all():
    all_recommendations = []

    for code, name in service_names.items():
        recs = get_recommendations(rules, code, top_n=3)

        # If no recommendations found
        if not recs or len(recs) == 0:
            all_recommendations.append({
                "input_service": name,
                "recommendations": [{
                    "recommended_service": "No recommendations found",
                    "support": "-",
                    "confidence": "-",
                    "lift": "-"
                }]
            })
            continue

        # Handle both dict or string outputs safely
        rec_list = []
        for r in recs:
            if isinstance(r, dict):  # when get_recommendations returns dicts
                rec_list.append({
                    "recommended_service": r.get("recommended_service_name", "Unknown"),
                    "support": round(r.get("support", 0), 3),
                    "confidence": round(r.get("confidence", 0), 3),
                    "lift": round(r.get("lift", 0), 3)
                })
            else:  # fallback if it’s just a string
                rec_list.append({
                    "recommended_service": str(r),
                    "support": "-",
                    "confidence": "-",
                    "lift": "-"
                })

        all_recommendations.append({
            "input_service": name,
            "recommendations": rec_list
        })

    return render_template("test_all.html", all_recommendations=all_recommendations)



if __name__ == "__main__":
    app.run(debug=True)
