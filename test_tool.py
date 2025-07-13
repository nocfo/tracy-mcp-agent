"""from adapters.ytj_adapter import YTJAdapter
import pprint

ytj = YTJAdapter()

print("🔍 Fetching company details...")
result = ytj.fetch_company_details("1805485-9")
print("✅ Result from V3:")
print(result)

print("\n🔍 Searching companies with keyword 'KPMG'...")
search_result = ytj.search_companies("KPMG")
print("✅ Search result:")
print(search_result)


print("🔍 Testing industry peer and partner lookup for 1805485-9")
result = ytj.find_industry_peers_and_partners("1805485-9")
pprint.pprint(result)"""


from adapters.chronos_adapter import forecast_company_metric
import matplotlib.pyplot as plt
import io
import base64

def test_forecast():
    result = forecast_company_metric("TechNova", "cash_and_cash_equivalents", forecast_periods=12)
    print("历史数据：", result["historical"])
    print("预测数据：", result["forecast"])

    img_data = base64.b64decode(result["plot_base64"])
    img = plt.imread(io.BytesIO(img_data), format='png')
    plt.imshow(img)
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    test_forecast()
