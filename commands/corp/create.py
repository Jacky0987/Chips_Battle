from commands.base import Command

class CorpCreateCommand(Command):
    name = "corp create"
    aliases = []
    description = "Create a company"

    def execute(self, name, industry_code):
        # Call company_service.create_company(current_user, name, industry_code)
        pass 