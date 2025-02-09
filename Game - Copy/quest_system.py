class QuestSystem():
    def __init__(self):
        self.quests = {
            "kill_enemies": {
                "description": "Kill 10 enemies",
                "target": 10,
                "progress": 0,
                "reward": 100
            },
            "collect_items": {
                "description": "Collect 5 potions",
                "target": 5,
                "progress": 0,
                "reward": 50
            }
        }
        self.active_quests = []
        self.completed_quests = []
        
    def update(self):
        for quest in self.active_quests:
            if self.quests[quest]["progress"] >= self.quests[quest]["target"]:
                self.complete_quest(quest)