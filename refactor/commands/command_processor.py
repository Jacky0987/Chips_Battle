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
        # 简化command_map，只保留基本映射
        # 大部分命令处理逻辑仍在process_command方法的if-elif语句中
        
        # 添加向导状态管理
        self.active_wizard = None
        self.wizard_type = None

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
                # 普通股票分析
                self.app.show_technical_analysis(symbol)
            else:
                self.app.print_to_output("用法: analysis <股票代码>", '#FF0000')
        elif cmd == 'chart':
            if len(parts) >= 2:
                symbol = parts[1].upper()
                time_range = parts[2] if len(parts) >= 3 else '5d'
                # 普通股票图表
                self.app.show_chart(symbol, time_range)
            else:
                self.app.print_to_output("用法: chart <股票代码> [时间范围]", '#FF0000')
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
            
        # 公司系统命令
        elif cmd == 'company':
            self._process_company_command(' '.join(parts[1:]))
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
            self._process_home_command(' '.join(parts[1:]))

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
                
                if subcommand == 'create':
                    # 支持简单命令创建和向导创建
                    if len(parts) >= 4:
                        # 传统方式：company create <公司名> <行业> [描述]
                        company_name = parts[2]
                        industry = parts[3]
                        description = ' '.join(parts[4:]) if len(parts) > 4 else ""
                        
                        success, message = self.app.company_manager.create_company(
                            self.app.user_manager.current_user, company_name, industry, description
                        )
                        color = '#00FF00' if success else '#FF0000'
                        self.app.print_to_output(message, color)
                    else:
                        # 新方式：启动创建向导
                        self._launch_company_creation_wizard()
                        
                elif subcommand == 'wizard':
                    # 直接启动创建向导
                    self._launch_company_creation_wizard()
                    
                elif subcommand == 'gui':
                    # 启动公司管理GUI
                    self._launch_company_gui()
                    
                elif subcommand == 'market':
                    # 显示公司市场
                    result = self.app.company_manager.show_company_market()
                    self.app.print_to_output(result, '#AAFFFF')
                    
                elif subcommand == 'my':
                    # 显示我的公司
                    result = self.app.company_manager.show_user_companies(self.app.user_manager.current_user)
                    self.app.print_to_output(result, '#AAFFFF')
                    
                elif subcommand == 'info':
                    if len(parts) < 2:
                        self.app.print_to_output("用法: company info <公司ID/股票代码>", '#FFAA00')
                        return
                    result = self.app.company_manager.show_company_info(parts[1])
                    self.app.print_to_output(result, '#AAFFFF')
                    
                elif subcommand == 'ipo':
                    if len(parts) < 4:
                        self.app.print_to_output("用法: company ipo <公司ID> <IPO价格> <发行股数>", '#FFAA00')
                        return
                        
                    company_identifier = parts[1]
                    ipo_price = float(parts[2])
                    shares = int(parts[3])
                    
                    # 使用智能查找
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    success, message = self.app.company_manager.apply_ipo(target_company.company_id, ipo_price, shares)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                    
                elif subcommand == 'invest':
                    if len(parts) < 3:
                        self.app.print_to_output("用法: company invest <公司ID> <注资金额>", '#FFAA00')
                        self.app.print_to_output("💡 注资将从个人账户转入公司账户", '#AAFFFF')
                        return
                        
                    company_identifier = parts[1]
                    try:
                        amount = float(parts[2])
                    except ValueError:
                        self.app.print_to_output("❌ 请输入有效的注资金额", '#FF0000')
                        return
                    
                    # 使用智能查找
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    # 检查个人账户余额
                    if amount > self.app.cash:
                        self.app.print_to_output(f"❌ 个人账户余额不足，当前余额: J${self.app.cash:,.0f}", '#FF0000')
                        return
                    
                    # 从个人账户扣除资金并向公司注资
                    self.app.cash -= amount
                    success, message = target_company.invest_capital(amount)
                    
                    if success:
                        # 保存公司数据
                        self.app.company_manager.save_companies()
                        self.app.print_to_output(message, '#00FF00')
                        self.app.print_to_output(f"💼 个人账户余额: J${self.app.cash:,.0f}", '#AAFFFF')
                    else:
                        # 回退个人账户资金
                        self.app.cash += amount
                        self.app.print_to_output(message, '#FF0000')
                        
                elif subcommand == 'account':
                    if len(parts) < 2:
                        self.app.print_to_output("用法: company account <公司ID>", '#FFAA00')
                        return
                        
                    company_identifier = parts[1]
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    account_info = target_company.get_company_account_info()
                    self.app.print_to_output(account_info, '#AAFFFF')
                    
                elif subcommand == 'hire':
                    if len(parts) < 3:
                        self.app.print_to_output("用法: company hire <公司ID> <职位> [候选人ID]", '#FFAA00')
                        self.app.print_to_output("示例: company hire JCTV 工程师", '#FFAA00')
                        self.app.print_to_output("      company hire JCTV 工程师 2  # 选择第2个候选人", '#FFAA00')
                        return
                        
                    company_identifier = parts[1]
                    position = parts[2]
                    
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    # 如果指定了候选人ID，直接招聘
                    if len(parts) >= 4:
                        try:
                            candidate_id = int(parts[3])
                            # 获取候选人列表
                            candidates = target_company.get_hire_candidates(position)
                            
                            if 1 <= candidate_id <= len(candidates):
                                selected_candidate = candidates[candidate_id - 1]
                                success, message = target_company.hire_staff_from_candidates(selected_candidate)
                                color = '#00FF00' if success else '#FF0000'
                                self.app.print_to_output(message, color)
                                
                                if success:
                                    self.app.company_manager.save_companies()
                            else:
                                self.app.print_to_output(f"❌ 候选人ID无效，请选择1-{len(candidates)}之间的数字", '#FF0000')
                                
                        except ValueError:
                            self.app.print_to_output("❌ 请输入有效的候选人ID", '#FF0000')
                        return
                    
                    # 显示候选人列表
                    candidates = target_company.get_hire_candidates(position)
                    
                    candidates_text = f"""
📋 {position} 候选人列表 - {target_company.name}

"""
                    
                    for i, candidate in enumerate(candidates, 1):
                        risk_display = f" ⚠️ {', '.join(candidate['risks'])}" if candidate['risks'] else ""
                        skills_display = f" 💼 {', '.join(candidate['special_skills'])}" if candidate['special_skills'] else ""
                        
                        candidates_text += f"""[{i}] {candidate['name']} 
    💰 期望薪资: J${candidate['salary']:,.0f}/月
    📊 综合评分: {candidate['total_score']:.1f}
    🎯 工作表现: {candidate['performance']:.1f}/100
    📚 工作经验: {candidate['experience']}年
    👥 领导能力: {candidate['leadership']:.1f}/100  
    💡 创新能力: {candidate['innovation']:.1f}/100{skills_display}{risk_display}
    
"""
                    
                    candidates_text += f"""
💡 使用方法: company hire {company_identifier} {position} <候选人编号>
示例: company hire {company_identifier} {position} 1
"""
                    
                    self.app.print_to_output(candidates_text, '#AAFFFF')
                    
                elif subcommand == 'staff':
                    if len(parts) < 2:
                        self.app.print_to_output("用法: company staff <公司ID>", '#FFAA00')
                        return
                        
                    company_identifier = parts[1]
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    staff_info = self._show_staff_list(target_company)
                    self.app.print_to_output(staff_info, '#AAFFFF')
                    
                elif subcommand == 'fire':
                    if len(parts) < 3:
                        self.app.print_to_output("用法: company fire <公司ID> <员工ID>", '#FFAA00')
                        return
                        
                    company_identifier = parts[1]
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    try:
                        employee_id = int(parts[2])
                        success, message = target_company.fire_employee(employee_id)
                        color = '#00FF00' if success else '#FF0000'
                        self.app.print_to_output(message, color)
                        if success:
                            self.app.company_manager.save_companies()
                    except ValueError:
                        self.app.print_to_output("❌ 员工ID必须是数字", '#FF0000')
                    
                elif subcommand == 'develop':
                    if len(parts) < 3:
                        self.app.print_to_output("用法: company develop <公司ID> <发展类型>", '#FFAA00')
                        self.app.print_to_output("发展类型: research, marketing, expansion, efficiency, technology, talent, brand, innovation", '#FFAA00')
                        return
                        
                    company_identifier = parts[1]
                    development_type = parts[2]
                    
                    # 使用智能查找，只在用户公司中查找
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        # 提供详细的错误信息和建议
                        user_companies = self.app.company_manager.get_user_companies(self.app.user_manager.current_user)
                        if user_companies:
                            suggestions = []
                            for uc in user_companies:
                                suggestions.append(f"  • {uc.name}: 【{uc.company_id}】/【{uc.symbol}】")
                            suggestions_text = "\n".join(suggestions)
                            
                            error_msg = f"""❌ 未找到您拥有的公司: {company_identifier}

💡 您拥有的公司:
{suggestions_text}

🔍 示例用法:
  company develop {user_companies[0].company_id} marketing
  company develop {user_companies[0].symbol} research"""
                            self.app.print_to_output(error_msg, '#FF0000')
                        else:
                            self.app.print_to_output("❌ 您还没有创建任何公司", '#FF0000')
                            self.app.print_to_output("💡 请先使用 'company wizard' 创建公司", '#FFAA00')
                        return
                    
                    success, message = self.app.company_manager.develop_company(target_company.company_id, development_type)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                    
                elif subcommand == 'acquire':
                    if len(parts) < 3:
                        self.app.print_to_output("用法:", '#FFAA00')
                        self.app.print_to_output("  company acquire <收购方ID> <目标股票代码>     # 评估收购价格", '#FFAA00')
                        self.app.print_to_output("  company acquire <收购方ID> <目标股票代码> confirm  # 确认收购", '#FFAA00')
                        return
                        
                    acquirer_id = parts[1]
                    target_symbol = parts[2]
                    
                    if len(parts) >= 4 and parts[3].lower() == 'confirm':
                        # 确认收购
                        success, message = self.app.company_manager.confirm_acquire_company(acquirer_id, target_symbol)
                        color = '#00FF00' if success else '#FF0000'
                        self.app.print_to_output(message, color)
                    else:
                        # 评估收购价格
                        success, message = self.app.company_manager.evaluate_acquisition(acquirer_id, target_symbol)
                        color = '#AAFFFF' if success else '#FF0000'
                        self.app.print_to_output(message, color)
                    
                elif subcommand == 'joint':
                    if len(parts) < 4:
                        self.app.print_to_output("用法: company joint <公司ID> <合作伙伴代码> <投资金额>", '#FFAA00')
                        return
                        
                    company_id = parts[1]
                    partner_symbol = parts[2]
                    investment = float(parts[3])
                    
                    success, message = self.app.company_manager.start_joint_venture(company_id, partner_symbol, investment)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                    
                elif subcommand == 'analysis':
                    if len(parts) < 2:
                        self.app.print_to_output("用法: company analysis <公司ID/股票代码>", '#FFAA00')
                        self.app.print_to_output("💡 支持JC股票技术分析和公司竞争分析", '#AAFFFF')
                        return
                
                    identifier = parts[1].upper()
                    
                    # 检查是否为JC股票代码
                    jc_company = self.app.company_manager.get_company_by_symbol(identifier)
                    if jc_company:
                        # 显示JC股票专业分析
                        self.app.show_jc_stock_analysis(identifier)
                    else:
                        # 显示公司竞争分析
                        result = self.app.company_manager.show_company_competition_analysis(identifier)
                        self.app.print_to_output(result, '#AAFFFF')
                    
                elif subcommand == 'news':
                    if len(parts) < 2:
                        self.app.print_to_output("用法: company news <公司ID>", '#FFAA00')
                        return
                        
                    result = self.app.company_manager.show_company_news(parts[1])
                    self.app.print_to_output(result, '#AAFFFF')
                    
                elif subcommand == 'chart':
                    if len(parts) < 2:
                        self.app.print_to_output("用法: company chart <股票代码> [时间范围]", '#FFAA00')
                        self.app.print_to_output("💡 专门显示JC股票技术图表", '#AAFFFF')
                        self.app.print_to_output("📊 时间范围: 1d, 5d, 1m, 3m, 6m, 1y", '#AAFFFF')
                        return
                    
                    symbol = parts[1].upper()
                    time_range = parts[2] if len(parts) >= 3 else '5d'
                    
                    # 检查是否为JC股票
                    jc_company = self.app.company_manager.get_company_by_symbol(symbol)
                    if jc_company:
                        # 显示JC股票专业图表
                        self.app.show_jc_stock_chart(symbol, time_range)
                    else:
                        self.app.print_to_output(f"❌ '{symbol}' 不是JC股票代码", '#FF0000')
                        # 显示可用的JC股票列表
                        if hasattr(self.app.company_manager, 'jc_stock_updater'):
                            available_stocks = self.app.company_manager.jc_stock_updater.get_available_jc_stocks()
                            if available_stocks:
                                self.app.print_to_output(f"💡 可用JC股票: {', '.join(available_stocks)}", '#AAFFFF')
                
                elif subcommand == 'industry':
                    if len(parts) < 2:
                        self.app.print_to_output("用法: company industry <行业名称>", '#FFAA00')
                        return
                        
                    result = self.app.company_manager.get_industry_report(parts[1])
                    self.app.print_to_output(result, '#AAFFFF')
                    
                elif subcommand == 'help':
                    help_text = self._get_company_help()
                    self.app.print_to_output(help_text, '#AAFFFF')
                    
                else:
                    self.app.print_to_output(f"❌ 未知的公司命令: {subcommand}", '#FF0000')
                    help_text = self._get_company_help()
                    self.app.print_to_output(help_text, '#AAFFFF')
                    
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

    def _process_company_command(self, command):
        """处理公司系统命令"""
        parts = command.split()
        if not parts:
            result = self.app.company_manager.show_company_market()
            self.app.print_to_output(result, '#AAFFFF')
            return
            
        action = parts[0]
        
        try:
            if action == 'create':
                # 支持简单命令创建和向导创建
                if len(parts) >= 4:
                    # 传统方式：company create <公司名> <行业> [描述]
                    company_name = parts[1]
                    industry = parts[2]
                    description = ' '.join(parts[3:]) if len(parts) > 3 else ""
                    
                    success, message = self.app.company_manager.create_company(
                        self.app.user_manager.current_user, company_name, industry, description
                    )
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                else:
                    # 新方式：启动创建向导
                    self._launch_company_creation_wizard()
                    
            elif action == 'wizard':
                # 直接启动创建向导
                self._launch_company_creation_wizard()
                
            elif action == 'gui':
                # 启动公司管理GUI
                self._launch_company_gui()
                
            elif action == 'market':
                # 显示公司市场
                result = self.app.company_manager.show_company_market()
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'my':
                # 显示我的公司
                result = self.app.company_manager.show_user_companies(self.app.user_manager.current_user)
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'info':
                if len(parts) < 2:
                    self.app.print_to_output("用法: company info <公司ID/股票代码>", '#FFAA00')
                    return
                result = self.app.company_manager.show_company_info(parts[1])
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'ipo':
                if len(parts) < 4:
                    self.app.print_to_output("用法: company ipo <公司ID> <IPO价格> <发行股数>", '#FFAA00')
                    return
                    
                company_identifier = parts[1]
                ipo_price = float(parts[2])
                shares = int(parts[3])
                
                # 使用智能查找
                target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                
                if not target_company:
                    self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                    return
                
                success, message = self.app.company_manager.apply_ipo(target_company.company_id, ipo_price, shares)
                color = '#00FF00' if success else '#FF0000'
                self.app.print_to_output(message, color)
                
            elif action == 'offering':
                # 增发股票功能
                if len(parts) < 4:
                    self.app.print_to_output("📋 股票增发命令使用方法:", '#FFAA00')
                    self.app.print_to_output("  company offering <公司ID> <增发价格> <增发股数>", '#FFAA00')
                    self.app.print_to_output("", '#FFAA00')
                    self.app.print_to_output("📖 示例:", '#AAFFFF')
                    self.app.print_to_output("  company offering JCTV 30.00 1000000  # 以30元增发100万股", '#AAFFFF')
                    self.app.print_to_output("", '#AAFFFF')
                    self.app.print_to_output("💡 注意:", '#FFAA00')
                    self.app.print_to_output("  • 只有已上市公司才能增发股票", '#FFAA00')
                    self.app.print_to_output("  • 增发价格不能偏离市价±50%", '#FFAA00')
                    self.app.print_to_output("  • 单次增发不超过现有股本50%", '#FFAA00')
                    return
                    
                try:
                    company_identifier = parts[1]
                    offering_price = float(parts[2])
                    shares_to_issue = int(parts[3])
                    
                    # 使用智能查找
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    success, message = self.app.company_manager.secondary_offering(target_company.company_id, offering_price, shares_to_issue)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                except ValueError:
                    self.app.print_to_output("❌ 增发价格和股数必须是数字", '#FF0000')
                    
            elif action == 'invest':
                if len(parts) < 3:
                    self.app.print_to_output("用法: company invest <公司ID> <注资金额>", '#FFAA00')
                    self.app.print_to_output("💡 注资将从个人账户转入公司账户", '#AAFFFF')
                    return
                    
                company_identifier = parts[1]
                try:
                    amount = float(parts[2])
                except ValueError:
                    self.app.print_to_output("❌ 请输入有效的注资金额", '#FF0000')
                    return
                
                # 使用智能查找
                target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                
                if not target_company:
                    self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                    return
                
                # 检查个人账户余额
                if amount > self.app.cash:
                    self.app.print_to_output(f"❌ 个人账户余额不足，当前余额: J${self.app.cash:,.0f}", '#FF0000')
                    return
                
                # 从个人账户扣除资金并向公司注资
                self.app.cash -= amount
                success, message = target_company.invest_capital(amount)
                
                if success:
                    # 保存公司数据
                    self.app.company_manager.save_companies()
                    self.app.print_to_output(message, '#00FF00')
                    self.app.print_to_output(f"💼 个人账户余额: J${self.app.cash:,.0f}", '#AAFFFF')
                else:
                    # 回退个人账户资金
                    self.app.cash += amount
                    self.app.print_to_output(message, '#FF0000')
                    
            elif action == 'account':
                if len(parts) < 2:
                    self.app.print_to_output("用法: company account <公司ID>", '#FFAA00')
                    return
                    
                company_identifier = parts[1]
                target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                
                if not target_company:
                    self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                    return
                
                account_info = target_company.get_company_account_info()
                self.app.print_to_output(account_info, '#AAFFFF')
                
            elif action == 'hire':
                if len(parts) < 3:
                    self.app.print_to_output("用法: company hire <公司ID> <职位> [候选人ID]", '#FFAA00')
                    self.app.print_to_output("示例: company hire JCTV 工程师", '#FFAA00')
                    self.app.print_to_output("      company hire JCTV 工程师 2  # 选择第2个候选人", '#FFAA00')
                    return
                    
                company_identifier = parts[1]
                position = parts[2]
                
                target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                
                if not target_company:
                    self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                    return
                
                # 如果指定了候选人ID，直接招聘
                if len(parts) >= 4:
                    try:
                        candidate_id = int(parts[3])
                        # 获取候选人列表
                        candidates = target_company.get_hire_candidates(position)
                        
                        if 1 <= candidate_id <= len(candidates):
                            selected_candidate = candidates[candidate_id - 1]
                            success, message = target_company.hire_staff_from_candidates(selected_candidate)
                            color = '#00FF00' if success else '#FF0000'
                            self.app.print_to_output(message, color)
                            
                            if success:
                                self.app.company_manager.save_companies()
                        else:
                            self.app.print_to_output(f"❌ 候选人ID无效，请选择1-{len(candidates)}之间的数字", '#FF0000')
                            
                    except ValueError:
                        self.app.print_to_output("❌ 请输入有效的候选人ID", '#FF0000')
                    return
                
                # 显示候选人列表
                candidates = target_company.get_hire_candidates(position)
                
                candidates_text = f"""
📋 {position} 候选人列表 - {target_company.name}

"""
                
                for i, candidate in enumerate(candidates, 1):
                    risk_display = f" ⚠️ {', '.join(candidate['risks'])}" if candidate['risks'] else ""
                    skills_display = f" 💼 {', '.join(candidate['special_skills'])}" if candidate['special_skills'] else ""
                    
                    candidates_text += f"""[{i}] {candidate['name']} 
    💰 期望薪资: J${candidate['salary']:,.0f}/月
    📊 综合评分: {candidate['total_score']:.1f}
    🎯 工作表现: {candidate['performance']:.1f}/100
    📚 工作经验: {candidate['experience']}年
    👥 领导能力: {candidate['leadership']:.1f}/100  
    💡 创新能力: {candidate['innovation']:.1f}/100{skills_display}{risk_display}
    
"""
                
                candidates_text += f"""
💡 使用方法: company hire {company_identifier} {position} <候选人编号>
示例: company hire {company_identifier} {position} 1
"""
                
                self.app.print_to_output(candidates_text, '#AAFFFF')
                
            elif action == 'staff':
                if len(parts) < 2:
                    self.app.print_to_output("用法: company staff <公司ID>", '#FFAA00')
                    return
                    
                company_identifier = parts[1]
                target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                
                if not target_company:
                    self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                    return
                
                staff_info = self._show_staff_list(target_company)
                self.app.print_to_output(staff_info, '#AAFFFF')
                
            elif action == 'expand':
                if len(parts) < 3:
                    self.app.print_to_output("用法: company expand budget <公司ID> <扩张预算>", '#FFAA00')
                    self.app.print_to_output("      company expand amount <公司ID> <员工数量>", '#FFAA00')
                    self.app.print_to_output("💡 budget: 根据预算自动配置职位结构", '#AAFFFF')
                    self.app.print_to_output("💡 amount: 快速扩张指定人数（单次最多50人）", '#AAFFFF')
                    self.app.print_to_output("📊 公司总员工数上限: 10,000人", '#AAFFFF')
                    return
                
                expand_type = parts[1]
                company_identifier = parts[2]
                
                if expand_type == 'budget':
                    # 按预算扩张
                    if len(parts) < 4:
                        self.app.print_to_output("用法: company expand budget <公司ID> <扩张预算>", '#FFAA00')
                        return
                    
                    try:
                        expansion_budget = float(parts[3])
                    except ValueError:
                        self.app.print_to_output("❌ 请输入有效的扩张预算", '#FF0000')
                        return
                    
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    success, message = target_company.batch_expand_staff(expansion_budget)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                    
                    if success:
                        self.app.company_manager.save_companies()
                        
                elif expand_type == 'amount':
                    # 按人数扩张
                    if len(parts) < 4:
                        self.app.print_to_output("用法: company expand amount <公司ID> <员工数量>", '#FFAA00')
                        return
                    
                    try:
                        staff_amount = int(parts[3])
                    except ValueError:
                        self.app.print_to_output("❌ 请输入有效的员工数量", '#FF0000')
                        return
                    
                    if staff_amount <= 0 or staff_amount > 50:
                        self.app.print_to_output("❌ 单次扩张数量必须在1-50人之间", '#FF0000')
                        return
                    
                    target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                    
                    if not target_company:
                        self.app.print_to_output(f"❌ 未找到您拥有的公司: {company_identifier}", '#FF0000')
                        return
                    
                    success, message = target_company.batch_expand_by_amount(staff_amount)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                    
                    if success:
                        self.app.company_manager.save_companies()
                        
                else:
                    self.app.print_to_output(f"❌ 未知的扩张类型: {expand_type}", '#FF0000')
                    self.app.print_to_output("支持的类型: budget (按预算), amount (按人数)", '#FFAA00')
                
            elif action == 'develop':
                if len(parts) < 3:
                    self.app.print_to_output("用法: company develop <公司ID> <发展类型>", '#FFAA00')
                    self.app.print_to_output("发展类型: research, marketing, expansion, efficiency, technology, talent, brand, innovation", '#FFAA00')
                    return
                    
                company_identifier = parts[1]
                development_type = parts[2]
                
                # 使用智能查找，只在用户公司中查找
                target_company = self.app.company_manager.find_company_by_identifier(company_identifier, user_only=True)
                
                if not target_company:
                    # 提供详细的错误信息和建议
                    user_companies = self.app.company_manager.get_user_companies(self.app.user_manager.current_user)
                    if user_companies:
                        suggestions = []
                        for uc in user_companies:
                            suggestions.append(f"  • {uc.name}: 【{uc.company_id}】/【{uc.symbol}】")
                        suggestions_text = "\n".join(suggestions)
                        
                        error_msg = f"""❌ 未找到您拥有的公司: {company_identifier}

💡 您拥有的公司:
{suggestions_text}

🔍 示例用法:
  company develop {user_companies[0].company_id} marketing
  company develop {user_companies[0].symbol} research"""
                        self.app.print_to_output(error_msg, '#FF0000')
                    else:
                        self.app.print_to_output("❌ 您还没有创建任何公司", '#FF0000')
                        self.app.print_to_output("💡 请先使用 'company wizard' 创建公司", '#FFAA00')
                    return
                
                success, message = self.app.company_manager.develop_company(target_company.company_id, development_type)
                color = '#00FF00' if success else '#FF0000'
                self.app.print_to_output(message, color)
                
            elif action == 'acquire':
                if len(parts) < 3:
                    self.app.print_to_output("用法:", '#FFAA00')
                    self.app.print_to_output("  company acquire <收购方ID> <目标股票代码>     # 评估收购价格", '#FFAA00')
                    self.app.print_to_output("  company acquire <收购方ID> <目标股票代码> confirm  # 确认收购", '#FFAA00')
                    return
                    
                acquirer_id = parts[1]
                target_symbol = parts[2]
                
                if len(parts) >= 4 and parts[3].lower() == 'confirm':
                    # 确认收购
                    success, message = self.app.company_manager.confirm_acquire_company(acquirer_id, target_symbol)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                else:
                    # 评估收购价格
                    success, message = self.app.company_manager.evaluate_acquisition(acquirer_id, target_symbol)
                    color = '#AAFFFF' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                
            elif action == 'joint':
                if len(parts) < 4:
                    self.app.print_to_output("用法: company joint <公司ID> <合作伙伴代码> <投资金额>", '#FFAA00')
                    return
                    
                company_id = parts[1]
                partner_symbol = parts[2]
                investment = float(parts[3])
                
                success, message = self.app.company_manager.start_joint_venture(company_id, partner_symbol, investment)
                color = '#00FF00' if success else '#FF0000'
                self.app.print_to_output(message, color)
                
            elif action == 'sell':
                # 公司出售功能
                if len(parts) < 2:
                    self.app.print_to_output("📋 公司出售命令使用方法:", '#FFAA00')
                    self.app.print_to_output("  company sell <公司ID或股票代码>          # 查看估值报告", '#FFAA00')
                    self.app.print_to_output("  company sell <公司ID或股票代码> <价格>   # 执行出售", '#FFAA00')
                    self.app.print_to_output("", '#FFAA00')
                    self.app.print_to_output("📖 示例:", '#AAFFFF')
                    self.app.print_to_output("  company sell MYCO          # 查看估值", '#AAFFFF')
                    self.app.print_to_output("  company sell MYCO 5000000  # 以500万出售", '#AAFFFF')
                    return
                    
                company_id = parts[1]
                
                if len(parts) == 2:
                    # 查看估值
                    success, message = self.app.company_manager.sell_company(company_id)
                    color = '#AAFFFF' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                    
                elif len(parts) == 3:
                    # 执行出售
                    try:
                        sale_price = float(parts[2])
                        success, message = self.app.company_manager.sell_company(company_id, sale_price)
                        color = '#00FF00' if success else '#FF0000'
                        self.app.print_to_output(message, color)
                    except ValueError:
                        self.app.print_to_output("❌ 出售价格必须是数字", '#FF0000')
                        
            elif action == 'close':
                # 公司关闭功能
                if len(parts) < 2:
                    self.app.print_to_output("📋 公司关闭命令使用方法:", '#FFAA00')
                    self.app.print_to_output("  company close <公司ID或股票代码>        # 预览关闭", '#FFAA00')
                    self.app.print_to_output("  company close <公司ID或股票代码> force  # 确认关闭", '#FFAA00')
                    self.app.print_to_output("", '#FFAA00')
                    self.app.print_to_output("📖 示例:", '#AAFFFF')
                    self.app.print_to_output("  company close MYCO        # 查看关闭预览", '#AAFFFF')
                    self.app.print_to_output("  company close MYCO force  # 确认关闭", '#AAFFFF')
                    self.app.print_to_output("", '#AAFFFF')
                    self.app.print_to_output("💡 提示: 关闭前建议先考虑出售，可能获得更好收益！", '#FFAA00')
                    return
                    
                company_id = parts[1]
                
                if len(parts) == 2:
                    # 预览关闭
                    success, message = self.app.company_manager.close_company(company_id)
                    color = '#FFAA00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                    
                elif len(parts) >= 3 and parts[2].lower() == 'force':
                    # 确认关闭
                    success, message = self.app.company_manager.close_company(company_id, force=True)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                
            elif action == 'delist':
                # 退市功能
                if len(parts) < 2:
                    self.app.print_to_output("📋 公司退市命令使用方法:", '#FFAA00')
                    self.app.print_to_output("  company delist <公司ID或股票代码>          # 查看退市预览", '#FFAA00')
                    self.app.print_to_output("  company delist <公司ID或股票代码> confirm  # 确认退市", '#FFAA00')
                    self.app.print_to_output("", '#FFAA00')
                    self.app.print_to_output("📖 示例:", '#AAFFFF')
                    self.app.print_to_output("  company delist JCTV         # 查看退市预览", '#AAFFFF')
                    self.app.print_to_output("  company delist JCTV confirm # 确认退市", '#AAFFFF')
                    self.app.print_to_output("", '#AAFFFF')
                    self.app.print_to_output("⚠️  注意: 退市需要支付股东补偿和退市费用！", '#FFAA00')
                    return
                    
                company_id = parts[1]
                
                if len(parts) == 2:
                    # 查看退市预览
                    success, message = self.app.company_manager.delist_company(company_id)
                    color = '#AAFFFF' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                    
                elif len(parts) >= 3 and parts[2].lower() == 'confirm':
                    # 确认退市
                    success, message = self.app.company_manager.confirm_delist_company(company_id)
                    color = '#00FF00' if success else '#FF0000'
                    self.app.print_to_output(message, color)
                
            elif action == 'detail':
                # 公司详细信息功能
                if len(parts) < 2:
                    self.app.print_to_output("📋 公司详情命令使用方法:", '#FFAA00')
                    self.app.print_to_output("  company detail <公司ID或股票代码>", '#FFAA00')
                    self.app.print_to_output("", '#FFAA00')
                    self.app.print_to_output("📖 示例:", '#AAFFFF')
                    self.app.print_to_output("  company detail JCTV    # 查看JCTV详细信息", '#AAFFFF')
                    self.app.print_to_output("  company detail 1       # 查看公司1详情", '#AAFFFF')
                    return
                    
                company_id = parts[1]
                success, message = self.app.company_manager.get_company_detail(company_id)
                color = '#AAFFFF' if success else '#FF0000'
                self.app.print_to_output(message, color)
                
            elif action == 'analysis':
                if len(parts) < 2:
                    self.app.print_to_output("用法: company analysis <公司ID/股票代码>", '#FFAA00')
                    self.app.print_to_output("💡 支持JC股票技术分析和公司竞争分析", '#AAFFFF')
                    return
                
                identifier = parts[1].upper()
                
                # 检查是否为JC股票代码
                jc_company = self.app.company_manager.get_company_by_symbol(identifier)
                if jc_company:
                    # 显示JC股票专业分析
                    self.app.show_jc_stock_analysis(identifier)
                else:
                    # 显示公司竞争分析
                    result = self.app.company_manager.show_company_competition_analysis(identifier)
                    self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'news':
                if len(parts) < 2:
                    self.app.print_to_output("用法: company news <公司ID>", '#FFAA00')
                    return
                    
                result = self.app.company_manager.show_company_news(parts[1])
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'chart':
                if len(parts) < 2:
                    self.app.print_to_output("用法: company chart <股票代码> [时间范围]", '#FFAA00')
                    self.app.print_to_output("💡 专门显示JC股票技术图表", '#AAFFFF')
                    self.app.print_to_output("📊 时间范围: 1d, 5d, 1m, 3m, 6m, 1y", '#AAFFFF')
                    return
                
                symbol = parts[1].upper()
                time_range = parts[2] if len(parts) >= 3 else '5d'
                
                # 检查是否为JC股票
                jc_company = self.app.company_manager.get_company_by_symbol(symbol)
                if jc_company:
                    # 显示JC股票专业图表
                    self.app.show_jc_stock_chart(symbol, time_range)
                else:
                    self.app.print_to_output(f"❌ '{symbol}' 不是JC股票代码", '#FF0000')
                    # 显示可用的JC股票列表
                    if hasattr(self.app.company_manager, 'jc_stock_updater'):
                        available_stocks = self.app.company_manager.jc_stock_updater.get_available_jc_stocks()
                        if available_stocks:
                            self.app.print_to_output(f"💡 可用JC股票: {', '.join(available_stocks)}", '#AAFFFF')
                
            elif action == 'industry':
                if len(parts) < 2:
                    self.app.print_to_output("用法: company industry <行业名称>", '#FFAA00')
                    return
                    
                result = self.app.company_manager.get_industry_report(parts[1])
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'help':
                help_text = self._get_company_help()
                self.app.print_to_output(help_text, '#AAFFFF')
                
            else:
                self.app.print_to_output(f"❌ 未知的公司命令: {action}", '#FF0000')
                help_text = self._get_company_help()
                self.app.print_to_output(help_text, '#AAFFFF')
                
        except Exception as e:
            self.app.print_to_output(f"❌ 公司命令执行出错: {str(e)}", '#FF0000')
            import traceback
            traceback.print_exc()

    def _launch_company_creation_wizard(self):
        """启动公司创建向导"""
        try:
            from company.company_creation import CompanyCreationWizard
            
            # 创建公司创建向导
            self.active_wizard = CompanyCreationWizard(self.app)
            self.wizard_type = "company_creation"
            
            # 启动向导并显示欢迎界面
            welcome_message = self.active_wizard.start_creation()
            self.app.print_to_output(welcome_message, '#00FFFF')
            
            # 提示用户如何开始
            self.app.print_to_output("\n💡 请输入 'start' 开始创建流程，或输入 'help' 查看帮助", '#FFAA00')
            
        except ImportError as e:
            self.app.print_to_output(f"无法启动公司创建向导: {str(e)}", '#FF0000')
        except Exception as e:
            self.app.print_to_output(f"启动公司创建向导失败: {str(e)}", '#FF0000')
            
    def _launch_company_gui(self):
        """启动公司管理GUI"""
        try:
            from company.company_gui import CompanyGUI
            
            # 检查是否有公司可以管理
            user_companies = self.app.company_manager.get_user_companies(self.app.user_manager.current_user)
            
            if not user_companies:
                self.app.print_to_output("您还没有创建任何公司", '#FFAA00')
                self.app.print_to_output("请先使用 'company wizard' 创建公司", '#FFAA00')
                return
            
            # 创建公司GUI
            company_gui = CompanyGUI(self.app)
            company_gui.open_company_center()
            
            self.app.print_to_output("🚀 公司管理界面已启动", '#00FF00')
            
        except ImportError as e:
            self.app.print_to_output(f"无法启动公司管理GUI: {str(e)}", '#FF0000')
        except Exception as e:
                            self.app.print_to_output(f"启动公司管理GUI失败: {str(e)}", '#FF0000')
    
    def _show_staff_list(self, company) -> str:
        """显示员工列表"""
        if not company.staff_list:
            return f"""
👥 {company.name} - 员工管理

📋 当前状态:
  员工总数: 0人
  员工上限: {company.max_staff}人
  月薪支出: J$0
  
💡 招聘提示:
  使用 'company hire {company.company_id} <姓名> <职位> <月薪>' 招聘员工
  使用 'company expand amount {company.company_id} <人数>' 批量招聘（单次最多50人）
  招聘需要提前支付3个月薪资作为保证金
"""
        
        staff_info = f"""
👥 {company.name} - 员工管理

📊 员工概况:
  员工总数: {len(company.staff_list)}/{company.max_staff}人
  月薪总支出: J${sum(staff['salary'] for staff in company.staff_list):,.0f}
  平均表现: {sum(staff['performance'] for staff in company.staff_list) / len(company.staff_list):.1f}/100
  平均经验: {sum(staff['experience'] for staff in company.staff_list) / len(company.staff_list):.1f}年

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                   📋 员工详细信息                                   
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # 表头
        staff_info += f"{'ID':<4} {'姓名':<12} {'职位':<15} {'月薪':<12} {'表现':<8} {'经验':<8} {'入职日期':<12}\n"
        staff_info += "─" * 80 + "\n"
        
        # 员工列表
        for staff in company.staff_list:
            hire_date = staff['hire_date'][:10]  # 只取日期部分
            staff_info += f"{staff['id']:<4} {staff['name']:<12} {staff['position']:<15} J${staff['salary']:>9,.0f} {staff['performance']:>6.1f}/100 {staff['experience']:>6}年 {hire_date:<12}\n"
        
        staff_info += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 财务分析:
  月薪支出: J${sum(staff['salary'] for staff in company.staff_list):,.0f}
  人均薪资: J${sum(staff['salary'] for staff in company.staff_list) / len(company.staff_list):,.0f}
  年薪支出: J${sum(staff['salary'] for staff in company.staff_list) * 12:,.0f}

🎯 团队效率:
  高表现员工(>90): {len([s for s in company.staff_list if s['performance'] > 90])}人
  标准表现员工(70-90): {len([s for s in company.staff_list if 70 <= s['performance'] <= 90])}人
  待改进员工(<70): {len([s for s in company.staff_list if s['performance'] < 70])}人

💡 管理建议:
  • 定期评估员工表现，及时调整薪资和职位
  • 高表现员工是公司的核心资产，应重点保留
  • 考虑为表现优秀的员工提供晋升机会
  • 员工数量接近上限时，考虑扩大办公场所
"""
        
        return staff_info
    
    def _get_company_help(self) -> str:
        """获取公司系统帮助信息"""
        return """
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                          💼 公司管理系统 - 完整指南                                             
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

🏗️  公司创建与基础管理:
  company wizard                           - 🧙‍♂️ 启动公司创建向导 (推荐新手使用)
  company create <公司名> <行业> [描述]      - ⚡ 快速创建公司
  company my                               - 📋 查看我的公司列表
  company market                           - 🏢 浏览公司市场
  company info <公司ID/代码>               - 📊 查看公司基本信息
  company detail <公司ID/代码>             - 🔍 查看公司详细信息（全面版）

💰 资金管理:
  company account <公司ID>                 - 💼 查看公司账户状况
  company invest <公司ID> <金额>           - 💰 个人向公司注资 (从个人账户转入)

👥 员工管理:
  company hire <公司ID> <职位>             - 📋 查看关键职位候选人列表
  company hire <公司ID> <职位> <候选人ID>  - ✅ 招聘指定候选人
  company expand budget <公司ID> <预算>    - 💰 按预算批量招聘扩张
  company expand amount <公司ID> <人数>    - 🚀 按人数快速扩张 (最多50人)
  company staff <公司ID>                  - 👥 查看员工详情和统计
  company fire <公司ID> <员工ID>           - 🔥 解雇员工 (支付遣散费)

💼 运营发展 (使用公司账户资金):
  company develop <公司ID> <发展类型>      - 🚀 投资公司发展

📊 发展类型说明:
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 类型         │ 成本基准        │ 主要效果                    │ 风险等级 │ 推荐阶段        │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ research     │ 营收4%/50万最低  │ 💡 提升利润10-20%，增长率+3%  │ 低      │ 初创期-成长期    │
│ marketing    │ 营收6%/80万最低  │ 📈 营收提升8-15%，市场份额+  │ 低      │ 所有阶段        │
│ expansion    │ 营收10%/120万最低│ 🏢 员工+15-25%，新增业务点   │ 中      │ 成长期-成熟期    │
│ efficiency   │ 员工*2万/30万最低│ ⚡ 效率+6-12%，成本削减3-8%  │ 低      │ 成熟期优先      │
│ technology   │ 营收5%/100万最低 │ 🔧 技术升级，营收+8-15%     │ 中      │ 科技公司优先     │
│ talent       │ 员工*5万/50万最低│ 🎓 人才培养，新增员工10-20% │ 低      │ 快速发展期      │
│ brand        │ 营收3%/80万最低  │ 🏆 品牌价值，市场份额+      │ 低      │ 消费行业优先     │
│ innovation   │ 营收8%/150万最低 │ 💫 创新研发，高收益高风险   │ 高      │ 技术密集行业     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

📈 资本运作:
  company ipo <公司ID> <价格> <股数>       - 🎯 申请IPO上市
  company offering <公司ID> <价格> <股数>  - 📈 增发股票（已上市公司）
  company delist <公司ID> [confirm]        - 📤 撤回IPO退市（需支付补偿）
  company acquire <收购方ID> <目标代码>     - 🔍 评估收购价格和可行性
  company acquire <收购方ID> <目标代码> confirm - 🤝 确认执行收购
  company joint <公司ID> <合作伙伴> <投资额> - 🤝 启动合资项目
  company sell <公司ID> [价格]             - 💰 出售公司（支持上市和未上市）
  company close <公司ID> [force]           - 🏢 关闭/解散公司

📊 专业分析 (JC股票专用):
  company analysis <股票代码>             - 📈 JC股票技术分析和基本面分析
  company chart <股票代码> [时间范围]      - 📊 JC股票专业技术图表

📰 信息查询:
  company analysis <公司ID>                - 🔍 公司竞争分析 (传统企业分析)
  company news <公司ID>                    - 📰 查看公司新闻
  company analysis <公司ID>               - 📊 竞争分析报告
  company industry <行业名>               - 🏭 行业分析报告

🆕 独立账户系统特色:
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ • 💼 公司账户与个人账户完全分离                                                                               │
│ • 💰 develop 操作使用公司资金，现实商业模拟                                                                  │
│ • 👥 员工招聘需要预付3个月薪资保证金                                                                          │
│ • 📊 智能候选人系统：不同能力、薪资期望、特殊技能                                                             │
│ • 🏢 expansion发展包含员工扩张功能                                                                           │
│ • 🚀 批量扩张：一键配置多层级人才结构                                                                        │
│ • ⚡ 资金不足时提供具体注资建议                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🎯 两种招聘模式说明:
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🔸 精准招聘 (company hire):                                                                                   │
│   • 适用于关键职位招聘                                                                                        │
│   • 详细候选人信息，能力评估                                                                                  │
│   • 手动选择最适合的人才                                                                                      │
│   • 适合小规模、高价值岗位                                                                                    │
│                                                                                                               │
│ 🔸 批量扩张 (company expand):                                                                                 │
│   • budget模式: 根据预算自动配置职位结构，智能成本控制                                                         │
│   • amount模式: 快速扩张指定人数（1-50人），适合规模化发展                                                     │
│   • 自动配置职位层级，根据公司规模调整                                                                        │
│   • 快速建立团队，高效率招聘                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🎮 使用流程建议:
  1️⃣ 使用 company wizard 创建公司
  2️⃣ 使用 company invest 向公司注资
  3️⃣ 使用 company expand 批量招聘建立团队
  4️⃣ 使用 company hire 精准招聘关键人才
  5️⃣ 使用 company develop 投资业务发展
  6️⃣ 监控 company account 财务状况
  7️⃣ 条件成熟时申请 company ipo 上市

💡 高级技巧:
  • 不同发展类型有行业加成，选择适合自己行业的发展方向
  • expansion 发展可以同时扩张员工数量
  • 优秀员工(表现>85)会为公司带来额外效率提升
  • 批量扩张会根据公司规模自动配置合理的职位结构
  • 小公司(20人以下)重基础岗位，大公司(100人以上)含管理层
  • 定期查看 news 和 analysis 了解市场动态
  • 合理控制薪资支出，避免现金流问题

🔧 技术支持:
  company help                             - 📖 显示此帮助信息
  company gui                              - 🖥️ 启动图形界面 (实验功能)

═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
"""

    def process_wizard_input(self, user_input: str):
        """处理向导输入"""
        if not self.active_wizard:
            return False
            
        try:
            if self.wizard_type == "company_creation":
                # 处理特殊的开始命令
                if user_input.lower() == 'start' and self.active_wizard.current_step == "welcome":
                    # 手动前进到第一个真正的步骤
                    self.active_wizard.current_step = "basic_info"
                    continue_wizard, response = True, self.active_wizard._get_current_step_display()
                else:
                    continue_wizard, response = self.active_wizard.process_input(user_input)
                
                self.app.print_to_output(response, '#00FFFF')
                
                if not continue_wizard:
                    # 向导完成或取消
                    self.active_wizard = None
                    self.wizard_type = None
                    
                return True
                
        except Exception as e:
            self.app.print_to_output(f"向导处理错误: {str(e)}", '#FF0000')
            self.active_wizard = None
            self.wizard_type = None
            
        return False

    def _process_home_command(self, command):
        """处理家庭投资系统命令"""
        parts = command.split()
        if not parts:
            result = self.app.home_manager.show_home_menu()
            self.app.print_to_output(result, '#AAFFFF')
            return
            
        action = parts[0]
        
        try:
            if action == 'real_estate' or action == 'property':
                result = self.app.home_manager.show_real_estate_market()
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'art':
                result = self.app.home_manager.show_art_collection_market()
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'luxury':
                result = self.app.home_manager.show_luxury_consumption()
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'services':
                result = self.app.home_manager.show_lifestyle_services()
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'club':
                if len(parts) > 1 and parts[1] == 'events':
                    self.app.print_to_output("俱乐部活动功能开发中...", '#FFAA00')
                else:
                    result = self.app.home_manager.show_club_memberships()
                    self.app.print_to_output(result, '#AAFFFF')
                    
            elif action == 'buy':
                if len(parts) < 3:
                    self.app.print_to_output("用法: home buy <类型> <ID> [数量]", '#FFAA00')
                    self.app.print_to_output("类型: real_estate, art, luxury, etf, car, service", '#FFAA00')
                    return
                    
                item_type = parts[1]
                item_id = parts[2]
                quantity = int(parts[3]) if len(parts) > 3 else 1
                
                if item_type == 'real_estate' or item_type == 'property':
                    success, message = self.app.home_manager.buy_real_estate(item_id, quantity)
                elif item_type == 'luxury':
                    success, message = self.app.home_manager.buy_luxury_item(item_id, quantity)
                elif item_type == 'service':
                    success, message = self.app.home_manager.buy_service(item_id)
                elif item_type == 'etf':
                    success, message = self.app.home_manager.buy_asset('etf', item_id, quantity)
                elif item_type == 'car':
                    success, message = self.app.home_manager.buy_asset('cars', item_id, quantity)
                else:
                    self.app.print_to_output(f"未知的投资类型: {item_type}", '#FF0000')
                    return
                    
                color = '#00FF00' if success else '#FF0000'
                self.app.print_to_output(message, color)
                
            elif action == 'sell':
                if len(parts) < 4:
                    self.app.print_to_output("用法: home sell <类型> <ID> <数量>", '#FFAA00')
                    return
                    
                item_type = parts[1]
                item_id = parts[2]
                quantity = int(parts[3])
                
                if item_type == 'etf':
                    success, message = self.app.home_manager.sell_asset('etf', item_id, quantity)
                elif item_type == 'car':
                    success, message = self.app.home_manager.sell_asset('cars', item_id, quantity)
                else:
                    self.app.print_to_output("该类型资产暂不支持出售", '#FFAA00')
                    return
                    
                color = '#00FF00' if success else '#FF0000'
                self.app.print_to_output(message, color)
                
            elif action == 'join':
                if len(parts) < 3 or parts[1] != 'club':
                    self.app.print_to_output("用法: home join club <俱乐部ID>", '#FFAA00')
                    return
                    
                club_id = parts[2]
                success, message = self.app.home_manager.join_club(club_id)
                color = '#00FF00' if success else '#FF0000'
                self.app.print_to_output(message, color)
                
            elif action == 'portfolio':
                result = self.app.home_manager.show_portfolio()
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'interior':
                result = self.app.home_manager.show_home_interior()
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'etf':
                result = self.app.home_manager.show_etf_market()
                self.app.print_to_output(result, '#AAFFFF')
                
            elif action == 'cars':
                result = self.app.home_manager.show_cars_market()
                self.app.print_to_output(result, '#AAFFFF')
                
            else:
                self.app.print_to_output(f"未知的家庭投资命令: {action}", '#FF0000')
                self.app.print_to_output("可用命令: real_estate, art, luxury, services, club, buy, sell, join, portfolio, interior, etf, cars", '#FFAA00')
                
        except ValueError as e:
            self.app.print_to_output(f"参数错误: {str(e)}", '#FF0000')
        except Exception as e:
            self.app.print_to_output(f"命令执行失败: {str(e)}", '#FF0000') 