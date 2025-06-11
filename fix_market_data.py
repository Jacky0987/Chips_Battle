#!/usr/bin/env python3
"""
市值数据修复工具
解决股价和市值不一致的问题
"""

import json
import os
from datetime import datetime

def fix_market_data():
    """修复市值数据"""
    data_file = 'data/jc_companies.json'
    
    if not os.path.exists(data_file):
        print("❌ 数据文件不存在")
        return
    
    # 读取数据
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔧 开始修复市值数据...")
    print(f"📂 找到 {len(data['companies'])} 家公司")
    
    fixed_count = 0
    public_companies = 0
    
    for company in data['companies']:
        if company.get('is_public', False):
            public_companies += 1
            symbol = company.get('symbol', '')
            stock_price = company.get('stock_price', 0)
            shares_outstanding = company.get('shares_outstanding', 0)
            old_market_cap = company.get('market_cap', 0)
            
            # 重新计算正确的市值
            correct_market_cap = stock_price * shares_outstanding
            
            print(f"📊 {symbol}: 股价 J${stock_price:.2f} × {shares_outstanding:,}股 = J${correct_market_cap:,.0f} (当前: J${old_market_cap:,.0f})")
            
            if abs(old_market_cap - correct_market_cap) > 1000:  # 差异超过1000
                company['market_cap'] = correct_market_cap
                fixed_count += 1
                print(f"   🔧 需要修复！差异: J${abs(old_market_cap - correct_market_cap):,.0f}")
            else:
                print(f"   ✅ 数据正确")
    
    print(f"\n📈 共检查了 {public_companies} 家上市公司")
    
    if fixed_count > 0:
        # 更新时间戳
        data['last_updated'] = datetime.now().isoformat()
        
        # 保存修复后的数据
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 修复完成！共修复了 {fixed_count} 家公司的市值数据")
    else:
        print("\n✅ 数据已正确，无需修复")

if __name__ == "__main__":
    fix_market_data() 