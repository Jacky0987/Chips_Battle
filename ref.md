    def update_stock_prices(self, print_callback=None):
        """Update stock prices with influence from market events."""
        while True:
            try:
                # Calculate market sentiment from recent events
                utc_now = datetime.now(pytz.UTC)  # Make datetime.now() UTC-aware
                recent_events = []
                
                # 安全地处理事件时间戳
                for event in self.market_events:
                    try:
                        timestamp_str = event.get('timestamp', '')
                        if timestamp_str:
                            # 处理各种时间戳格式
                            if timestamp_str.endswith('Z'):
                                timestamp_str = timestamp_str.replace('Z', '+00:00')
                            elif '+' not in timestamp_str and 'T' in timestamp_str:
                                timestamp_str += '+00:00'
                            
                            event_time = datetime.fromisoformat(timestamp_str)
                            if event_time.tzinfo is None:
                                event_time = pytz.UTC.localize(event_time)
                            
                            # 检查事件是否在最近一小时内
                            time_diff = (utc_now - event_time).total_seconds()
                            if time_diff < 3600:  # 1小时内
                                recent_events.append(event)
                    except (ValueError, TypeError) as e:
                        # 跳过无效的时间戳
                        print(f"警告: 无效的事件时间戳 {event.get('id', 'unknown')}: {e}")
                        continue
                
                sentiment_score = sum(1 for e in recent_events if e['impact']['effect'] == 'positive') - \
                                  sum(1 for e in recent_events if e['impact']['effect'] == 'negative')
                sentiment_factor = 1.0 + (sentiment_score * 0.005)

                # Map events to sectors and stocks
                event_impacts = {}
                for event in recent_events:
                    try:
                        for sector in event['impact']['sectors']:
                            if sector not in event_impacts:
                                event_impacts[sector] = []
                            event_impacts[sector].append(event['impact'])
                        for stock in event['related_stocks']:
                            if stock not in event_impacts:
                                event_impacts[stock] = []
                            event_impacts[stock].append(event['impact'])
                    except KeyError as e:
                        print(f"警告: 事件结构不完整 {event.get('id', 'unknown')}: 缺少 {e}")
                        continue

                # 安全地更新股票价格
                for symbol in list(self.stocks.keys()):  # 使用list()避免字典在迭代时被修改
                    try:
                        stock = self.stocks[symbol]
                        old_price = stock.get('price', 100.0)
                        volatility = stock.get('volatility', 0.02)
                        volume = stock.get('volume', 1000000)
                        beta = stock.get('beta', 1.0)

                        # Base price change
                        random_change = random.uniform(-volatility, volatility)
                        volume_factor = 1.0 - (min(volume, 100000000) / 100000000) * 0.1

                        # Apply event-based impact
                        event_factor = 1.0
                        sector = stock.get('sector', 'Other')
                        
                        if sector in event_impacts:
                            impacts = event_impacts[sector]
                            for impact in impacts:
                                magnitude = impact.get('magnitude', 0.01)
                                if impact.get('effect') == 'negative':
                                    magnitude = -magnitude
                                event_factor *= (1 + magnitude)
                                
                        if symbol in event_impacts:
                            impacts = event_impacts[symbol]
                            for impact in impacts:
                                magnitude = impact.get('magnitude', 0.01)
                                if impact.get('effect') == 'negative':
                                    magnitude = -magnitude
                                event_factor *= (1 + magnitude)

                        # Combine factors with safety limits
                        total_change = random_change * volume_factor * sentiment_factor * event_factor * beta
                        # 限制单次变化幅度
                        total_change = max(-0.1, min(0.1, total_change))  # 最大10%变化
                        
                        new_price = old_price * (1 + total_change)
                        if new_price < 1:
                            new_price = max(1, old_price * 0.99)

                        # Update stock data with safety checks
                        stock['price'] = round(new_price, 2)
                        stock['change'] = round(new_price - old_price, 2)
                        stock['volume'] = int(volume * random.uniform(0.8, 1.2))
                        
                        # 安全地更新价格历史
                        if 'price_history' not in stock:
                            stock['price_history'] = [old_price] * 20
                        stock['price_history'].append(stock['price'])
                        if len(stock['price_history']) > 20:
                            stock['price_history'].pop(0)
                            
                        stock['last_updated'] = datetime.now(pytz.UTC).isoformat()
                        
                        # 安全地计算PE比率
                        eps = stock.get('eps', 0)
                        if eps and eps > 0:
                            stock['pe_ratio'] = round(stock['price'] / eps, 2)
                        else:
                            stock['pe_ratio'] = None
                            
                    except Exception as e:
                        print(f"更新股票 {symbol} 价格时出错: {e}")
                        continue

                # 安全地保存数据
                try:
                    self.save_stocks()
                except Exception as e:
                    print(f"保存股票数据时出错: {e}")
                
                # 更新指数
                try:
                    self.update_indices()
                except Exception as e:
                    print(f"更新指数时出错: {e}")
                
            except Exception as e:
                print(f"价格更新循环出错: {e}")
                # 出错时等待更长时间再继续
                time.sleep(10)
                continue
            
            # 正常情况下的等待时间
            time.sleep(random.uniform(1, 3))