import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from service_names import service_names

def data_prep(df: pd.DataFrame) -> pd.DataFrame:
    df['Service'] = df['service_id'].astype(str) + '_' + df['category_id'].astype(str)
    df['create_date'] = pd.to_datetime(df['create_date'], dayfirst=True, errors='coerce')
    df['New_Date'] = df['create_date'].dt.strftime('%Y-%m')
    df['BasketId'] = df['user_id'].astype(str) + '_' + df['New_Date']
    return df

def generate_rules(df: pd.DataFrame, min_support=0.002, min_lift=0.5):
    apriori_df = (
        df.groupby(['BasketId', 'Service'])['category_id']
          .count()
          .unstack()
          .fillna(0)
          .applymap(lambda x: 1 if x > 0 else 0)
    )
    # Debug: Show what columns (service codes) are in the apriori dataframe
    print(f"📦 Apriori dataframe columns (service codes): {sorted(list(apriori_df.columns))[:10]}...")
    print(f"📦 Total unique services in data: {len(apriori_df.columns)}")
    
    frequent_itemsets = apriori(apriori_df, min_support=min_support, use_colnames=True, low_memory=True)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift)
    
    print(f"✅ Generated {len(rules)} association rules")
    return rules

def get_recommendations(rules_df: pd.DataFrame, service_code: str, top_n=3):
    print(f"🔎 Searching for service code: {service_code}")
    print(f"📋 Total rules available: {len(rules_df)}")
    
    if len(rules_df) == 0:
        print("⚠️ No rules generated!")
        return []
    
    # Debug: Show first few antecedents to understand format
    if len(rules_df) > 0:
        sample_antecedents = rules_df["antecedents"].iloc[0]
        print(f"📝 Sample antecedent format: {sample_antecedents} (type: {type(sample_antecedents)})")
        print(f"📝 Sample antecedent items: {list(sample_antecedents) if hasattr(sample_antecedents, '__iter__') else sample_antecedents}")
    
    sorted_rules = rules_df.sort_values("lift", ascending=False)
    
    # Check if service_code is in antecedents
    # Antecedents are frozensets, so we need to check membership correctly
    filtered = sorted_rules[sorted_rules["antecedents"].apply(lambda x: service_code in x if isinstance(x, (frozenset, set, list, tuple)) else False)]
    
    print(f"🔍 Found {len(filtered)} rules matching service code {service_code}")
    
    if len(filtered) == 0:
        # Debug: Show what service codes are actually in the rules
        all_antecedents = set()
        for ant in sorted_rules["antecedents"].head(10):
            if isinstance(ant, (frozenset, set)):
                all_antecedents.update(ant)
            elif isinstance(ant, (list, tuple)):
                all_antecedents.update(ant)
        print(f"📊 Sample service codes in rules: {sorted(list(all_antecedents))[:10]}")
    
    top_rules = filtered.head(top_n)

    # Return list of readable service names
    recommendation_list = []
    for _, row in top_rules.iterrows():
        consequent = list(row["consequents"])[0]
        service_name = service_names.get(consequent, f"Service {consequent}")
        recommendation_list.append(service_name)
    
    return recommendation_list
