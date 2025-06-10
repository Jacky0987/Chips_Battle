class CommandProcessor:
    def __init__(self, main_app):
        self.app = main_app
        # 导入帮助系统
        from .help_system import HelpSystem
        self.help_system = HelpSystem(main_app)
        self.available_commands = [
            'help', 'balance', 'list', 'buy', 'sell', 'portfolio', 'history',
            'quote', 'analysis', 'alerts', 'sector', 'risk', 'simulator',
            'market', 'news', 'leaderboard', 'achievements', 'profile',
            'settings', 'set', 'performance', 'chart', 'compare', 'install', 'uninstall',
            'appmarket.app', 'save', 'logout', 'clear', 'exit',
            # 新增高级交易命令
            'short', 'cover', 'orders', 'cancel', 'stop_loss', 'take_profit',
            'limit_buy', 'limit_sell', 'limit_short',
            # 新增高级功能命令
            'market_sentiment', 'economic_calendar', 'sector_chart',
            # 银行系统命令
            'bank',
            # 家庭投资系统命令
            'home',
            # 指数系统命令
            'index', 'indices',
            # 大宗商品交易系统命令
            'forex', 'futures', 'spot', 'commodity', 'commodities'
        ]
        self.admin_available_commands = [
            # 新分类命令
            "user", "stock", "bank", "system",
            # 旧命令格式（兼容性）
            "add_stock", "remove_stock", "modify_cash",
            "reset_user", "modify_stock_price", "view_all_users",
            "create_event", "ban_user", "admin_help", "exit", "exit_admin"
        ]

    def process_command(self, command):
        """处理用户输入的命令"""
        if not command.strip():
            return

        # 检查是否是管理员命令
        if command.startswith("sudo "):
            admin_command = command[5:].strip()
            if not admin_command:
                # sudo后面没有命令，显示帮助
                self.app.print_to_output("用法: sudo <管理员命令>", '#FF0000')
                self.app.print_to_output("输入 'sudo admin_help' 查看管理员命令列表", '#FFAA00')
                return
                
            if not self.app.admin_mode:
                self.app.verify_admin()
                # 验证成功后需要重新执行命令
                if self.app.admin_mode:
                    self.app.print_to_output(f"admin@stock-sim:~# {admin_command}", '#FF5500')
                    self.process_admin_command(admin_command)
                return
            else:
                self.app.print_to_output(f"admin@stock-sim:~# {admin_command}", '#FF5500')
                self.process_admin_command(admin_command)
                return
        elif command.lower() == "sudo":
            # 单独的sudo命令
            self.app.print_to_output("用法: sudo <管理员命令>", '#FF0000')
            self.app.print_to_output("输入 'sudo admin_help' 查看管理员命令列表", '#FFAA00')
            return

        # 显示命令提示符
        if self.app.admin_mode:
            self.app.print_to_output(f"admin@stock-sim:~# {command}", '#FF5500')
        else:
            self.app.print_to_output(f"trader@stock-sim:~$ {command}", '#FFFF00')

        parts = command.lower().split()
        cmd = parts[0] if parts else ""

        # 基础命令
        if cmd == 'help':
            # 支持帮助分类，如 help basic, help trading 等
            category = parts[1] if len(parts) >= 2 else None
            self.help_system.show_help(category)
        elif cmd == 'balance' or cmd == 'bal':
            self.app.show_balance()
        elif cmd == 'list':
            self.app.show_stock_list()
        elif cmd == 'buy':
            if len(parts) >= 3:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    self.app.buy_stock(symbol, quantity)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数", '#FF0000')
            else:
                self.app.print_to_output("用法: buy <股票代码> <数量>", '#FF0000')
        elif cmd == 'sell':
            if len(parts) >= 3:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    self.app.sell_stock(symbol, quantity)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数", '#FF0000')
            else:
                self.app.print_to_output("用法: sell <股票代码> <数量>", '#FF0000')
        elif cmd == 'portfolio' or cmd == 'port':
            self.app.show_portfolio()
        elif cmd == 'history' or cmd == 'hist':
            self.app.show_history()
        elif cmd == 'quote':
            if len(parts) >= 2:
                symbol = parts[1].upper()
                self.app.show_quote(symbol)
            else:
                self.app.print_to_output("用法: quote <股票代码>", '#FF0000')

        # 新增命令
        elif cmd == 'market':
            self.app.show_market_overview()
        elif cmd == 'news':
            self.app.show_market_news()
        elif cmd == 'leaderboard':
            sort_by = parts[1] if len(parts) >= 2 else 'total'
            self.app.show_leaderboard(sort_by)
        elif cmd == 'achievements':
            if len(parts) >= 2:
                sub_cmd = parts[1].lower()
                if sub_cmd == 'progress':
                    self.app.show_achievement_progress()
                elif sub_cmd in ['trading', 'profit', 'portfolio', 'wealth', 'loyalty', 'risk', 'advanced', 'banking', 'skill', 'special', 'progress', 'meta']:
                    self.app.show_achievements_by_category(sub_cmd)
                else:
                    self.app.show_achievements()
            else:
                self.app.show_achievements()
        elif cmd == 'profile':
            self.app.show_profile()
        elif cmd == 'analysis':
            if len(parts) >= 2:
                symbol = parts[1].upper()
                self.app.show_technical_analysis(symbol)
            else:
                self.app.print_to_output("用法: analysis <股票代码>", '#FF0000')
        elif cmd == 'alerts':
            self.app.show_alerts_menu()
        elif cmd == 'sector':
            self.app.show_sector_analysis()
        elif cmd == 'risk':
            self.app.show_risk_assessment()
        elif cmd == 'simulator':
            self.app.start_trading_simulator()
        
        # 新增高级命令
        elif cmd == 'settings':
            if len(parts) >= 2:
                sub_cmd = parts[1].lower()
                if sub_cmd == 'export':
                    self.app.export_settings()
                elif sub_cmd == 'import' and len(parts) >= 3:
                    filename = parts[2]
                    self.app.import_settings(filename)
                elif sub_cmd == 'reset':
                    self.app.reset_settings()
                else:
                    self.app.show_settings()
            else:
                self.app.show_settings()
        elif cmd == 'set':
            if len(parts) >= 3:
                setting_id = parts[1]
                value = parts[2]
                self.app.modify_setting(setting_id, value)
            else:
                self.app.print_to_output("用法: set <设置编号> <值>", '#FF0000')
        elif cmd == 'performance':
            self.app.show_performance()
        elif cmd == 'chart':
            if len(parts) >= 2:
                symbol = parts[1].upper()
                time_range = parts[2] if len(parts) >= 3 else 'day'
                self.app.show_chart(symbol, time_range)
            else:
                self.app.print_to_output("用法: chart <股票代码> [时间范围]", '#FF0000')
        elif cmd == 'compare':
            if len(parts) >= 3:
                symbol1 = parts[1].upper()
                symbol2 = parts[2].upper()
                self.app.compare_stocks(symbol1, symbol2)
            else:
                self.app.print_to_output("用法: compare <股票代码1> <股票代码2>", '#FF0000')
        elif cmd == 'install':
            if len(parts) >= 2:
                app_id = parts[1]
                result = self.app.app_market.install_app(app_id)
                self.app.print_to_output(result)
            else:
                self.app.print_to_output("用法: install <应用ID>", '#FF0000')
        elif cmd == 'uninstall':
            if len(parts) >= 2:
                app_id = parts[1]
                result = self.app.app_market.uninstall_app(app_id)
                self.app.print_to_output(result)
            else:
                self.app.print_to_output("用法: uninstall <应用ID>", '#FF0000')
        elif cmd == 'appmarket.app':
            if len(parts) >= 2:
                app_id = parts[1]
                args = parts[2:] if len(parts) > 2 else []
                result = self.app.app_market.run_app(app_id, *args)
                self.app.print_to_output(result)
            else:
                self.app.print_to_output("用法: appmarket.app <应用ID> [参数...]", '#FFAA00')
        
        # 系统命令
        elif cmd == 'save':
            self.app.save_game_data()
            self.app.print_to_output("✓ 游戏数据已保存", '#00FF00')
        elif cmd == 'logout':
            self.app.logout()
        elif cmd == 'clear':
            self.app.clear_screen()
        elif cmd == 'cls':
            self.app.clear_screen()
        elif cmd == 'exit':
            self.app.save_game_data()
            self.app.root.quit()

        # 大宗商品交易命令
        elif cmd == 'forex':
            result = self.app.commodity_trading.handle_forex_command(parts[1:])
            self.app.print_to_output(result)
        elif cmd == 'futures':
            result = self.app.commodity_trading.handle_futures_command(parts[1:])
            self.app.print_to_output(result)
        elif cmd == 'spot':
            result = self.app.commodity_trading.handle_spot_command(parts[1:])
            self.app.print_to_output(result)
        elif cmd == 'commodity' or cmd == 'commodities':
            result = self.app.commodity_trading.handle_commodity_command(parts[1:])
            self.app.print_to_output(result)

        # 新增高级交易命令
        elif cmd == 'limit_buy':
            if len(parts) >= 4:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    limit_price = float(parts[3])
                    self.app.buy_stock(symbol, quantity, "limit", limit_price)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数，价格必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: limit_buy <股票代码> <数量> <限价>", '#FF0000')
        elif cmd == 'limit_sell':
            if len(parts) >= 4:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    limit_price = float(parts[3])
                    self.app.sell_stock(symbol, quantity, "limit", limit_price)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数，价格必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: limit_sell <股票代码> <数量> <限价>", '#FF0000')
        elif cmd == 'short':
            if len(parts) >= 3:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    self.app.short_sell(symbol, quantity)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数", '#FF0000')
            else:
                self.app.print_to_output("用法: short <股票代码> <数量>", '#FF0000')
        elif cmd == 'limit_short':
            if len(parts) >= 4:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    limit_price = float(parts[3])
                    self.app.short_sell(symbol, quantity, "limit", limit_price)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数，价格必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: limit_short <股票代码> <数量> <限价>", '#FF0000')
        elif cmd == 'cover':
            if len(parts) >= 3:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    self.app.cover_short(symbol, quantity)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数", '#FF0000')
            else:
                self.app.print_to_output("用法: cover <股票代码> <数量>", '#FF0000')
        elif cmd == 'stop_loss':
            if len(parts) >= 4:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    stop_price = float(parts[3])
                    self.app.create_stop_loss(symbol, quantity, stop_price)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数，价格必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: stop_loss <股票代码> <数量> <止损价>", '#FF0000')
        elif cmd == 'take_profit':
            if len(parts) >= 4:
                try:
                    symbol = parts[1].upper()
                    quantity = int(parts[2])
                    target_price = float(parts[3])
                    self.app.create_take_profit(symbol, quantity, target_price)
                except ValueError:
                    self.app.print_to_output("错误: 数量必须是整数，价格必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: take_profit <股票代码> <数量> <目标价>", '#FF0000')
        elif cmd == 'orders':
            self.app.show_pending_orders()
        elif cmd == 'cancel':
            if len(parts) >= 2:
                order_id = parts[1]
                self.app.cancel_order(order_id)
            else:
                self.app.print_to_output("用法: cancel <订单号>", '#FF0000')

        # 高级功能命令 - 已实现的
        elif cmd == 'market_sentiment':
            self.app.show_market_sentiment()
        elif cmd == 'economic_calendar':
            self.app.show_economic_calendar()
        elif cmd == 'sector_chart':
            if len(parts) >= 2:
                sector_name = parts[1]
                self.app.show_sector_chart(sector_name)
            else:
                self.app.show_sector_chart()
        
        # 银行系统命令 - 已实现的
        elif cmd == 'bank':
            if len(parts) >= 2:
                bank_cmd = parts[1].lower()
                if bank_cmd == 'loan':
                    if len(parts) >= 3:
                        try:
                            amount = float(parts[2])
                            days = int(parts[3]) if len(parts) >= 4 else 30
                            self.app.apply_bank_loan(amount, days)
                        except ValueError:
                            self.app.print_to_output("错误: 无效的贷款参数", '#FF0000')
                    else:
                        self.app.print_to_output("用法: bank loan <金额> [天数]", '#FFAA00')
                elif bank_cmd == 'repay':
                    if len(parts) >= 3:
                        self.app.repay_bank_loan(parts[2])
                    else:
                        self.app.print_to_output("用法: bank repay <贷款ID>", '#FFAA00')
                elif bank_cmd == 'deposit':
                    if len(parts) >= 3:
                        try:
                            amount = float(parts[2])
                            term_type = parts[3] if len(parts) >= 4 else 'demand'
                            self.app.make_bank_deposit(amount, term_type)
                        except ValueError:
                            self.app.print_to_output("错误: 无效的存款参数", '#FF0000')
                    else:
                        self.app.print_to_output("用法: bank deposit <金额> [类型]", '#FFAA00')
                elif bank_cmd == 'withdraw':
                    if len(parts) >= 3:
                        self.app.withdraw_bank_deposit(parts[2])
                    else:
                        self.app.print_to_output("用法: bank withdraw <存款ID>", '#FFAA00')
                elif bank_cmd == 'emergency':
                    self.app.request_emergency_assistance()
                elif bank_cmd == 'contracts':
                    self.app.show_bank_contracts()
                elif bank_cmd == 'status':
                    self.app.show_bank_status()
                elif bank_cmd == 'rates':
                    self.app.show_bank_rates()
                elif bank_cmd == 'new' and len(parts) >= 3 and parts[2].lower() == 'contract':
                    self.app.generate_new_bank_contracts()
                else:
                    self.app.print_to_output("错误: 无效的银行命令", '#FF0000')
                    self.app.print_to_output("用法: bank <loan|repay|deposit|withdraw|emergency|contracts|status|rates|new contract>", '#FFAA00')
            else:
                self.app.show_banking_menu()
        
        # AppMarket系统命令
        elif cmd == 'appmarket':
            if len(parts) >= 2:
                action = parts[1].lower()
                if action == 'install' and len(parts) >= 3:
                    result = self.app.app_market.install_app(parts[2])
                    self.app.print_to_output(result)
                elif action == 'uninstall' and len(parts) >= 3:
                    result = self.app.app_market.uninstall_app(parts[2])
                    self.app.print_to_output(result)
                elif action == 'my':
                    result = self.app.app_market.show_my_apps()
                    self.app.print_to_output(result)
                elif action == 'usage':
                    result = self.app.app_market.show_usage_stats()
                    self.app.print_to_output(result)
                else:
                    # 显示特定类别
                    result = self.app.app_market.show_market(parts[1])
                    self.app.print_to_output(result)
            else:
                result = self.app.app_market.show_market()
                self.app.print_to_output(result)
        elif cmd == 'appmarket.app':
            if len(parts) >= 2:
                app_id = parts[1]
                args = parts[2:] if len(parts) > 2 else []
                result = self.app.app_market.run_app(app_id, *args)
                self.app.print_to_output(result)
            else:
                self.app.print_to_output("用法: appmarket.app <应用ID> [参数...]", '#FFAA00')

        # 家庭投资系统命令
        elif cmd == 'home':
            if len(parts) >= 2:
                action = parts[1].lower()
                if action == 'interior':
                    result = self.app.home_manager.show_home_interior()
                    self.app.print_to_output(result)
                elif action == 'etf':
                    result = self.app.home_manager.show_etf_market()
                    self.app.print_to_output(result)
                elif action == 'cars':
                    result = self.app.home_manager.show_cars_market()
                    self.app.print_to_output(result)
                elif action == 'portfolio':
                    result = self.app.home_manager.show_portfolio()
                    self.app.print_to_output(result)
                elif action == 'market':
                    # 显示综合市场信息
                    etf_result = self.app.home_manager.show_etf_market()
                    car_result = self.app.home_manager.show_cars_market()
                    self.app.print_to_output(etf_result + "\n" + car_result)
                elif action == 'buy' and len(parts) >= 5:
                    asset_type = parts[2]
                    asset_id = parts[3]
                    quantity = parts[4]
                    result = self.app.home_manager.buy_asset(asset_type, asset_id, quantity)
                    self.app.print_to_output(result)
                elif action == 'sell' and len(parts) >= 5:
                    asset_type = parts[2]
                    asset_id = parts[3]
                    quantity = parts[4]
                    result = self.app.home_manager.sell_asset(asset_type, asset_id, quantity)
                    self.app.print_to_output(result)
                elif action == 'info' and len(parts) >= 4:
                    asset_type = parts[2]
                    asset_id = parts[3]
                    if asset_type == 'etf' and asset_id in self.app.home_manager.etf_funds:
                        etf = self.app.home_manager.etf_funds[asset_id]
                        etf.update_price()
                        result = etf.get_detailed_info()
                        self.app.print_to_output(result)
                    elif asset_type == 'car' and asset_id in self.app.home_manager.luxury_cars:
                        car = self.app.home_manager.luxury_cars[asset_id]
                        car.update_price()
                        result = car.get_detailed_info()
                        self.app.print_to_output(result)
                    else:
                        self.app.print_to_output(f"❌ 资产 {asset_type} {asset_id} 不存在", '#FF0000')
                else:
                    self.app.print_to_output("❌ 无效的home命令格式", '#FF0000')
                    self.app.print_to_output("用法: home <etf|cars|portfolio|market|buy|sell|info> [参数...]", '#FFAA00')
            else:
                result = self.app.home_manager.show_home_menu()
                self.app.print_to_output(result)

        # 指数系统命令
        elif cmd == 'index' or cmd == 'indices':
            if len(parts) >= 2:
                sub_cmd = parts[1].lower()
                if sub_cmd == 'list':
                    self.app.show_index_list()
                elif sub_cmd == 'category' and len(parts) >= 3:
                    category = parts[2]
                    self.app.show_indices_by_category(category)
                elif sub_cmd == 'compare' and len(parts) >= 4:
                    index1 = parts[2].upper()
                    index2 = parts[3].upper()
                    self.app.compare_indices(index1, index2)
                else:
                    # 直接显示指数详情
                    index_code = parts[1].upper()
                    self.app.show_index_detail(index_code)
            else:
                self.app.show_indices_overview()

        # 银行系统命令
        elif cmd == 'bank':
            if hasattr(self.app, 'bank_manager'):
                if len(parts) < 2:
                    result = self.app.bank_manager.show_bank_system_menu()
                    self.app.print_to_output(result)
                    return
                    
                subcommand = parts[1].lower()
                
                if subcommand == 'list':
                    result = self.app.bank_manager.show_bank_list()
                    self.app.print_to_output(result)
                elif subcommand == 'select' and len(parts) >= 3:
                    bank_id = parts[2].upper()
                    result = self.app.bank_manager.select_bank(bank_id)
                    self.app.print_to_output(result)
                elif subcommand == 'tasks':
                    bank_id = parts[2].upper() if len(parts) >= 3 else None
                    result = self.app.bank_manager.show_bank_tasks(bank_id)
                    self.app.print_to_output(result)
                elif subcommand == 'accept' and len(parts) >= 3:
                    task_id = parts[2]
                    user_id = self.app.user_manager.current_user
                    success, message = self.app.bank_manager.task_manager.accept_task(user_id, task_id)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                elif subcommand == 'progress':
                    user_id = self.app.user_manager.current_user
                    active_tasks = self.app.bank_manager.task_manager.get_active_tasks(user_id)
                    
                    if not active_tasks:
                        self.app.print_to_output("📋 您目前没有进行中的银行任务", '#FFAA00')
                    else:
                        progress_text = "📋 任务进度详情:\n\n"
                        for task in active_tasks:
                            bank_name = self.app.bank_manager.banks[task.bank_id].name
                            progress = task._calculate_overall_progress()
                            progress_text += f"🏦 {task.title} ({bank_name})\n"
                            progress_text += f"   进度: {progress*100:.1f}% {'🟢' if progress > 0.7 else '🟡' if progress > 0.3 else '🔴'}\n"
                            progress_text += f"   截止: {task.deadline.strftime('%Y-%m-%d') if task.deadline else '无期限'}\n"
                            progress_text += f"   奖励: J${task.reward.cash_bonus:,.0f}\n\n"
                        self.app.print_to_output(progress_text)
                elif subcommand == 'complete' and len(parts) >= 3:
                    task_id = parts[2]
                    user_id = self.app.user_manager.current_user
                    success, message = self.app.bank_manager.task_manager.complete_task(user_id, task_id)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                elif subcommand == 'loan' and len(parts) >= 3:
                    try:
                        amount = float(parts[2])
                        bank_id = parts[3].upper() if len(parts) >= 4 else "JC_COMMERCIAL"
                        result = self.app.bank_manager.apply_loan(amount, bank_id)
                        self.app.print_to_output(result)
                    except ValueError:
                        self.app.print_to_output("❌ 无效的贷款金额", '#FF0000')
                elif subcommand == 'deposit' and len(parts) >= 3:
                    try:
                        amount = float(parts[2])
                        term_type = parts[3] if len(parts) >= 4 else 'demand'
                        bank_id = parts[4].upper() if len(parts) >= 5 else "JC_COMMERCIAL"
                        result = self.app.bank_manager.apply_deposit(amount, term_type, bank_id)
                        self.app.print_to_output(result)
                    except ValueError:
                        self.app.print_to_output("❌ 无效的存款金额", '#FF0000')
                elif subcommand == 'repay' and len(parts) >= 3:
                    loan_id = parts[2]
                    result = self.app.bank_manager.repay_loan(loan_id)
                    self.app.print_to_output(result)
                elif subcommand == 'withdraw' and len(parts) >= 3:
                    deposit_id = parts[2]
                    result = self.app.bank_manager.withdraw_deposit(deposit_id)
                    self.app.print_to_output(result)
                elif subcommand == 'status':
                    bank_id = parts[2].upper() if len(parts) >= 3 else None
                    result = self.app.bank_manager.show_account_summary(bank_id)
                    self.app.print_to_output(result)
                else:
                    result = self.app.bank_manager.show_bank_system_menu()
                    self.app.print_to_output(result)
            else:
                self.app.print_to_output("❌ 银行系统尚未初始化", '#FF0000')
                
        # 公司系统命令
        elif cmd == 'company':
            if hasattr(self.app, 'company_manager'):
                if len(parts) < 2:
                    result = self.app.company_manager.show_company_market()
                    self.app.print_to_output(result)
                    return
                    
                subcommand = parts[1].lower()
                
                if subcommand == 'create' and len(parts) >= 4:
                    company_name = parts[2]
                    industry = parts[3]
                    description = ' '.join(parts[4:]) if len(parts) > 4 else ""
                    user_id = self.app.user_manager.current_user
                    success, result = self.app.company_manager.create_company(user_id, company_name, industry, description)
                    self.app.print_to_output(result)
                elif subcommand == 'list':
                    user_id = self.app.user_manager.current_user
                    result = self.app.company_manager.show_user_companies(user_id)
                    self.app.print_to_output(result)
                elif subcommand == 'info' and len(parts) >= 3:
                    identifier = parts[2]
                    result = self.app.company_manager.show_company_info(identifier)
                    self.app.print_to_output(result)
                elif subcommand == 'ipo' and len(parts) >= 5:
                    try:
                        company_id = parts[2]
                        ipo_price = float(parts[3])
                        shares_to_issue = int(parts[4])
                        success, result = self.app.company_manager.apply_ipo(company_id, ipo_price, shares_to_issue)
                        self.app.print_to_output(result)
                    except ValueError:
                        self.app.print_to_output("❌ 无效的IPO参数", '#FF0000')
                elif subcommand == 'news' and len(parts) >= 3:
                    company_id = parts[2]
                    result = self.app.company_manager.show_company_news(company_id)
                    self.app.print_to_output(result)
                elif subcommand == 'develop' and len(parts) >= 4:
                    company_id = parts[2]
                    development_type = parts[3]
                    success, result = self.app.company_manager.develop_company(company_id, development_type)
                    self.app.print_to_output(result)
                elif subcommand == 'industry' and len(parts) >= 3:
                    industry = parts[2]
                    result = self.app.company_manager.get_industry_report(industry)
                    self.app.print_to_output(result)
                else:
                    result = self.app.company_manager.show_company_market()
                    self.app.print_to_output(result)
            else:
                self.app.print_to_output("❌ 公司系统尚未初始化", '#FF0000')

        # 管理员模式相关命令
        elif cmd == 'exit_admin' and self.app.admin_mode:
            self.app.exit_admin_mode()

        else:
            self.app.print_to_output(f"未知命令: {cmd}. 输入 'help' 查看可用命令.", '#FF0000')

    def process_admin_command(self, command):
        """处理管理员命令"""
        if not command.strip():
            self.app.print_to_output("请输入管理员命令，输入 'admin_help' 查看帮助", '#FF0000')
            return
            
        parts = command.split()
        cmd = parts[0].lower() if parts else ""

        if cmd == "admin_help" or cmd == "help":
            self.app.show_admin_help()
        elif cmd == "user":
            self._process_user_admin_command(parts[1:])
        elif cmd == "stock":
            self._process_stock_admin_command(parts[1:])
        elif cmd == "bank":
            self._process_bank_admin_command(parts[1:])
        elif cmd == "system":
            self._process_system_admin_command(parts[1:])
        # 保留旧命令格式兼容性
        elif cmd == "add_stock":
            if len(parts) >= 5:
                symbol = parts[1].upper()
                name = parts[2]
                try:
                    price = float(parts[3])
                    sector = parts[4]
                    volatility = float(parts[5]) if len(parts) >= 6 else 0.03
                    self.app.admin_add_stock(symbol, name, price, sector, volatility)
                except ValueError:
                    self.app.print_to_output("错误: 价格和波动率必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: add_stock <代码> <名称> <价格> <行业> [波动率]", '#FF0000')
        elif cmd == "remove_stock":
            if len(parts) >= 2:
                symbol = parts[1].upper()
                self.app.admin_remove_stock(symbol)
            else:
                self.app.print_to_output("用法: remove_stock <股票代码>", '#FF0000')
        elif cmd == "modify_stock_price":
            if len(parts) >= 3:
                symbol = parts[1].upper()
                try:
                    price = float(parts[2])
                    self.app.admin_modify_stock_price(symbol, price)
                except ValueError:
                    self.app.print_to_output("错误: 价格必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: modify_stock_price <股票代码> <新价格>", '#FF0000')
        elif cmd == "view_all_users":
            self.app.admin_view_all_users()
        elif cmd == "modify_cash":
            if len(parts) >= 3:
                username = parts[1]
                try:
                    amount = float(parts[2])
                    self.app.admin_modify_cash(username, amount)
                except ValueError:
                    self.app.print_to_output("错误: 金额必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: modify_cash <用户名> <金额变化>", '#FF0000')
                self.app.print_to_output("示例: modify_cash testuser 1000 (增加1000)", '#FFAA00')
                self.app.print_to_output("示例: modify_cash testuser -500 (减少500)", '#FFAA00')
        elif cmd == "reset_user":
            if len(parts) >= 2:
                username = parts[1]
                self.app.admin_reset_user(username)
            else:
                self.app.print_to_output("用法: reset_user <用户名>", '#FF0000')
        elif cmd == "create_event":
            if len(parts) >= 2:
                event_text = " ".join(parts[1:])
                self.app.create_market_event(event_text)
            else:
                self.app.print_to_output("用法: create_event <事件内容>", '#FF0000')
        elif cmd == "ban_user":
            if len(parts) >= 2:
                username = parts[1]
                self.app.ban_user(username)
            else:
                self.app.print_to_output("用法: ban_user <用户名>", '#FF0000')
        elif cmd == "exit" or cmd == "exit_admin":
            self.app.exit_admin_mode()
        else:
            self.app.print_to_output(f"未知管理员命令: {cmd}", '#FF0000')
            self.app.print_to_output("输入 'admin_help' 查看可用命令列表", '#FFAA00')

    def _process_user_admin_command(self, parts):
        """处理用户管理命令"""
        if not parts:
            self.app.print_to_output("用法: sudo user <子命令> [参数...]", '#FF0000')
            return
        
        subcmd = parts[0].lower()
        
        if subcmd == "list":
            self.app.admin_view_all_users()
        elif subcmd == "info":
            if len(parts) >= 2:
                username = parts[1]
                self.app.admin_get_user_info(username)
            else:
                self.app.print_to_output("用法: sudo user info <用户名>", '#FF0000')
        elif subcmd == "cash":
            if len(parts) >= 3:
                username = parts[1]
                try:
                    amount = float(parts[2])
                    self.app.admin_modify_cash(username, amount)
                except ValueError:
                    self.app.print_to_output("错误: 金额必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: sudo user cash <用户名> <金额>", '#FF0000')
        elif subcmd == "level":
            if len(parts) >= 3:
                username = parts[1]
                level = parts[2]
                self.app.admin_modify_user_level(username, level)
            else:
                self.app.print_to_output("用法: sudo user level <用户名> <等级>", '#FF0000')
        elif subcmd == "exp":
            if len(parts) >= 3:
                username = parts[1]
                experience = parts[2]
                self.app.admin_modify_user_experience(username, experience)
            else:
                self.app.print_to_output("用法: sudo user exp <用户名> <经验值>", '#FF0000')
        elif subcmd == "credit":
            if len(parts) >= 3:
                username = parts[1]
                credit_rating = parts[2]
                self.app.admin_modify_user_credit(username, credit_rating)
            else:
                self.app.print_to_output("用法: sudo user credit <用户名> <信用等级>", '#FF0000')
        elif subcmd == "reset":
            if len(parts) >= 2:
                username = parts[1]
                self.app.admin_reset_user(username)
            else:
                self.app.print_to_output("用法: sudo user reset <用户名>", '#FF0000')
        elif subcmd == "ban":
            if len(parts) >= 2:
                username = parts[1]
                self.app.ban_user(username)
            else:
                self.app.print_to_output("用法: sudo user ban <用户名>", '#FF0000')
        elif subcmd == "unban":
            if len(parts) >= 2:
                username = parts[1]
                self.app.admin_unban_user(username)
            else:
                self.app.print_to_output("用法: sudo user unban <用户名>", '#FF0000')
        else:
            self.app.print_to_output(f"未知用户管理命令: {subcmd}", '#FF0000')

    def _process_stock_admin_command(self, parts):
        """处理股票管理命令"""
        if not parts:
            self.app.print_to_output("用法: sudo stock <子命令> [参数...]", '#FF0000')
            return
        
        subcmd = parts[0].lower()
        
        if subcmd == "add":
            if len(parts) >= 5:
                symbol = parts[1].upper()
                name = parts[2]
                try:
                    price = float(parts[3])
                    sector = parts[4]
                    volatility = float(parts[5]) if len(parts) >= 6 else 0.03
                    self.app.admin_add_stock(symbol, name, price, sector, volatility)
                except ValueError:
                    self.app.print_to_output("错误: 价格和波动率必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: sudo stock add <代码> <名称> <价格> <行业> [波动率]", '#FF0000')
        elif subcmd == "remove":
            if len(parts) >= 2:
                symbol = parts[1].upper()
                self.app.admin_remove_stock(symbol)
            else:
                self.app.print_to_output("用法: sudo stock remove <代码>", '#FF0000')
        elif subcmd == "price":
            if len(parts) >= 3:
                symbol = parts[1].upper()
                try:
                    price = float(parts[2])
                    self.app.admin_modify_stock_price(symbol, price)
                except ValueError:
                    self.app.print_to_output("错误: 价格必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: sudo stock price <代码> <价格>", '#FF0000')
        elif subcmd == "info":
            if len(parts) >= 2:
                symbol = parts[1].upper()
                self.app.admin_get_stock_info(symbol)
            else:
                self.app.print_to_output("用法: sudo stock info <代码>", '#FF0000')
        elif subcmd == "list":
            self.app.admin_list_all_stocks()
        elif subcmd == "volatility":
            if len(parts) >= 3:
                symbol = parts[1].upper()
                try:
                    volatility = float(parts[2])
                    self.app.admin_modify_stock_volatility(symbol, volatility)
                except ValueError:
                    self.app.print_to_output("错误: 波动率必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: sudo stock volatility <代码> <波动率>", '#FF0000')
        else:
            self.app.print_to_output(f"未知股票管理命令: {subcmd}", '#FF0000')

    def _process_bank_admin_command(self, parts):
        """处理银行管理命令"""
        if not parts:
            self.app.print_to_output("用法: sudo bank <子命令> [参数...]", '#FF0000')
            return
        
        subcmd = parts[0].lower()
        
        if subcmd == "rates":
            if len(parts) >= 3:
                rate_type = parts[1].lower()
                try:
                    rate = float(parts[2])
                    if rate_type == "loan":
                        self.app.admin_modify_loan_rate(rate)
                    elif rate_type == "deposit":
                        self.app.admin_modify_deposit_rate(rate)
                    else:
                        self.app.print_to_output("错误: 利率类型必须是 loan 或 deposit", '#FF0000')
                except ValueError:
                    self.app.print_to_output("错误: 利率必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: sudo bank rates <loan|deposit> <利率>", '#FF0000')
        elif subcmd == "credit":
            if len(parts) >= 3:
                username = parts[1]
                credit_rating = parts[2]
                self.app.admin_modify_user_credit(username, credit_rating)
            else:
                self.app.print_to_output("用法: sudo bank credit <用户名> <信用等级>", '#FF0000')
        elif subcmd == "loan":
            if len(parts) >= 3:
                username = parts[1]
                try:
                    amount = float(parts[2])
                    days = int(parts[3]) if len(parts) >= 4 else 30
                    self.app.admin_force_loan(username, amount, days)
                except ValueError:
                    self.app.print_to_output("错误: 金额和天数必须是数字", '#FF0000')
            else:
                self.app.print_to_output("用法: sudo bank loan <用户名> <金额> [天数]", '#FF0000')
        elif subcmd == "forgive":
            if len(parts) >= 3:
                username = parts[1]
                loan_id = parts[2]
                self.app.admin_forgive_loan(username, loan_id)
            else:
                self.app.print_to_output("用法: sudo bank forgive <用户名> <贷款ID>", '#FF0000')
        else:
            self.app.print_to_output(f"未知银行管理命令: {subcmd}", '#FF0000')

    def _process_system_admin_command(self, parts):
        """处理系统管理命令"""
        if not parts:
            self.app.print_to_output("用法: sudo system <子命令> [参数...]", '#FF0000')
            return
        
        subcmd = parts[0].lower()
        
        if subcmd == "event":
            if len(parts) >= 2:
                event_text = " ".join(parts[1:])
                self.app.create_market_event(event_text)
            else:
                self.app.print_to_output("用法: sudo system event <事件内容>", '#FF0000')
        elif subcmd == "reset":
            if len(parts) >= 2 and parts[1].lower() == "market":
                self.app.admin_reset_market_prices()
            else:
                self.app.print_to_output("用法: sudo system reset market", '#FF0000')
        elif subcmd == "backup":
            self.app.admin_backup_system()
        elif subcmd == "maintenance":
            if len(parts) >= 2:
                mode = parts[1]
                self.app.admin_set_maintenance(mode)
            else:
                self.app.print_to_output("用法: sudo system maintenance <on|off>", '#FF0000')
        else:
            self.app.print_to_output(f"未知系统管理命令: {subcmd}", '#FF0000')



    def auto_complete(self, current_text):
        """命令自动补全功能"""
        if not current_text:
            return []

        # 确定使用哪个命令列表（普通模式或管理员模式）
        commands = self.admin_available_commands if self.app.admin_mode else self.available_commands

        # 查找匹配的命令
        matches = [cmd for cmd in commands if cmd.startswith(current_text)]
        return matches

    def find_common_prefix(self, strings):
        """查找字符串列表的共同前缀"""
        if not strings:
            return ""
        prefix = strings[0]
        for s in strings[1:]:
            while not s.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ""
        return prefix 