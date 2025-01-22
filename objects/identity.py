class CyberarkObject:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return f'{self.name}'

class Role(CyberarkObject):
    def __init__(self, role_data):
        super().__init__(role_data['Row']['ID'], role_data['Row']['Name'])
        self.orgpath = role_data['Row']['OrgPath']
        self.services_data = []

class Member(CyberarkObject):
    def __init__(self, name, type):
        super().__init__(f'{type}/{name}', name)
        self.type = type

class SafeMember(Member):
    def __init__(self, member_data):
        super().__init__(member_data['memberName'], member_data['memberType'])

class SIAPolicyRuleMember(Member):
    def __init__(self, name, type):
        super().__init__(name, type)

class RoleMember(Member):
    def __init__(self, member_data):
        super().__init__(member_data['Name'], 'Group')

class Safe(CyberarkObject):
    def __init__(self, safe_data):
        super().__init__(safe_data['safeUrlId'], safe_data['safeName'])
        self.members = []

class SCAPolicy(CyberarkObject):
    def __init__(self, policy_data):
        super().__init__(policy_data['policyId'], policy_data['name'])
        self.members = []

class SCAPolicyMember(Member):
    def __init__(self, policy_member_data):
        super().__init__(policy_member_data['entityName'], policy_member_data['entityClass'])

class SIAPolicy(CyberarkObject):
    def __init__(self, policy_data):
        super().__init__(policy_data['policyId'], policy_data['policyName'])
        self.rules = []

class SIAPolicyRule(CyberarkObject):
    def __init__(self, policy_rule_data, policy_name):
        super().__init__(policy_rule_data['ruleName'], policy_rule_data['ruleName'])
        self.members = []
        self.policy_name = policy_name

class Webapp(CyberarkObject):
    def __init__(self, webapp_data):
        super().__init__(webapp_data['ID'], webapp_data['Name'])