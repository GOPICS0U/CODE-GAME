import pygame
import random
import math
import os
from enum import Enum
import time

# Initialisation de Pygame
pygame.init()

# Définition des constantes
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 139)

# Constantes de jeu
MAX_HEALTH = 100
MAX_HUNGER = 100
MAX_THIRST = 100
MAX_ENERGY = 100
MAX_TEMPERATURE = 37.0  # température corporelle normale en °C


# Énumération pour les conditions météorologiques
class Weather(Enum):
    SUNNY = 1
    CLOUDY = 2
    RAINY = 3
    STORMY = 4
    SNOWY = 5


# Énumération pour les périodes de la journée
class TimeOfDay(Enum):
    MORNING = 1
    AFTERNOON = 2
    EVENING = 3
    NIGHT = 4


# Fonction pour charger les images
def load_image(name, scale=1.0):
    try:
        image = pygame.image.load(name)
        if scale != 1.0:
            original_size = image.get_size()
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except pygame.error:
        # Si l'image n'est pas trouvée, créer une surface avec un motif de placeholder
        size = (64, 64)
        image = pygame.Surface(size)
        for x in range(0, size[0], 8):
            for y in range(0, size[1], 8):
                color = (
                    (100, 100, 100) if (x // 8 + y // 8) % 2 == 0 else (150, 150, 150)
                )
                pygame.draw.rect(image, color, (x, y, 8, 8))

        # Ajouter le nom de l'image manquante
        font = pygame.font.SysFont(None, 15)
        text = font.render(os.path.basename(name), True, (255, 50, 50))
        text_rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
        image.blit(text, text_rect)

        if scale != 1.0:
            original_size = image.get_size()
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            image = pygame.transform.scale(image, new_size)
        return image


# Classe pour représenter l'inventaire du joueur


class Inventory:
    def __init__(self):
        self.items = {}
        self.max_weight = 20.0  # poids maximum en kg
        self.current_weight = 0.0

    def add_item(self, item, quantity=1):
        if self.current_weight + (item.weight * quantity) <= self.max_weight:
            if item.name in self.items:
                self.items[item.name] += quantity
            else:
                self.items[item.name] = quantity
            self.current_weight += item.weight * quantity
            return True
        else:
            return False

    def remove_item(self, item_name, quantity=1):
        if item_name in self.items and self.items[item_name] >= quantity:
            self.items[item_name] -= quantity
            item = next((i for i in Item.all_items if i.name == item_name), None)
            if item:
                self.current_weight -= item.weight * quantity
            if self.items[item_name] <= 0:
                del self.items[item_name]
            return True
        return False

    def has_item(self, item_name, quantity=1):
        return item_name in self.items and self.items[item_name] >= quantity


# Classe pour les objets du jeu
class Item:
    all_items = []

    def __init__(
        self,
        name,
        weight,
        description,
        icon_name=None,
        is_food=False,
        is_drinkable=False,
        is_weapon=False,
        is_tool=False,
        hunger_value=0,
        thirst_value=0,
        damage=0,
        durability=100,
    ):
        self.name = name
        self.weight = weight
        self.description = description
        self.icon_name = (
            icon_name if icon_name else f"icons/{name.lower().replace(' ', '_')}.png"
        )
        self.is_food = is_food
        self.is_drinkable = is_drinkable
        self.is_weapon = is_weapon
        self.is_tool = is_tool
        self.hunger_value = hunger_value
        self.thirst_value = thirst_value
        self.damage = damage
        self.durability = durability
        self.icon = (
            load_image(self.icon_name) if os.path.exists(self.icon_name) else None
        )
        if self.icon is None:
            # Créer une icône par défaut
            self.icon = pygame.Surface((64, 64))
            self.icon.fill(GRAY)
            font = pygame.font.SysFont(None, 20)
            text = font.render(name[:10], True, BLACK)
            text_rect = text.get_rect(center=(32, 32))
            self.icon.blit(text, text_rect)
        Item.all_items.append(self)

    @classmethod
    def initialize_items(cls):
        # Nourriture
        Item(
            "Baies",
            0.1,
            "Des baies sauvages comestibles.",
            is_food=True,
            hunger_value=5,
            thirst_value=2,
        )
        Item(
            "Viande crue",
            0.5,
            "De la viande crue. Mieux vaut la cuire avant de la manger.",
            is_food=True,
            hunger_value=10,
        )
        Item(
            "Viande cuite",
            0.5,
            "De la viande bien cuite.",
            is_food=True,
            hunger_value=30,
        )

        # Boisson
        Item(
            "Eau de pluie",
            0.5,
            "De l'eau de pluie recueillie.",
            is_drinkable=True,
            thirst_value=20,
        )
        Item(
            "Eau purifiée",
            0.5,
            "De l'eau potable et purifiée.",
            is_drinkable=True,
            thirst_value=40,
        )

        # Armes
        Item(
            "Couteau de fortune",
            0.3,
            "Un couteau rudimentaire fabriqué avec des matériaux trouvés.",
            is_weapon=True,
            is_tool=True,
            damage=10,
            durability=50,
        )
        Item(
            "Lance en bois",
            1.2,
            "Une lance taillée dans du bois.",
            is_weapon=True,
            damage=15,
            durability=30,
        )

        # Outils
        Item(
            "Hache de pierre",
            2.0,
            "Une hache primitive faite de pierre et de bois.",
            is_tool=True,
            durability=40,
        )
        Item(
            "Briquet",
            0.1,
            "Un briquet qui permet d'allumer un feu facilement.",
            is_tool=True,
            durability=100,
        )

        # Ressources
        Item("Bois", 1.0, "Du bois ramassé dans la forêt.")
        Item(
            "Pierre",
            0.8,
            "Une pierre qui peut être utilisée pour fabriquer des outils.",
        )
        Item("Corde", 0.2, "Une corde fabriquée à partir de fibres végétales.")


# Classe principale du joueur
class Player:
    def __init__(self, name):
        self.name = name
        self.health = MAX_HEALTH
        self.hunger = MAX_HUNGER
        self.thirst = MAX_THIRST
        self.energy = MAX_ENERGY
        self.body_temperature = MAX_TEMPERATURE
        self.inventory = Inventory()
        self.skills = {
            "Survie": 1,
            "Chasse": 1,
            "Construction": 1,
            "Cuisine": 1,
            "Combat": 1,
        }
        self.has_shelter = False
        self.has_fire = False
        self.fire_duration = 0
        self.message_log = []

        # Position visuelle pour le joueur
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2

        # Animation
        self.animation_frame = 0
        self.animation_time = 0

    def add_message(self, message):
        self.message_log.append(message)
        if len(self.message_log) > 10:  # Limiter à 10 messages
            self.message_log.pop(0)

    def update_stats(self, game):
        # Diminution naturelle des statistiques au fil du temps
        self.hunger -= 0.05 * game.time_scale
        self.thirst -= 0.1 * game.time_scale
        self.energy -= 0.03 * game.time_scale

        # Impact de la météo sur la température corporelle
        if game.current_weather == Weather.SNOWY:
            self.body_temperature -= 0.02 * game.time_scale
        elif game.current_weather == Weather.RAINY:
            self.body_temperature -= 0.01 * game.time_scale

        # Impact du moment de la journée sur la température
        if game.time_of_day == TimeOfDay.NIGHT:
            self.body_temperature -= 0.01 * game.time_scale

        # Impact du feu sur la température corporelle
        if self.has_fire:
            self.body_temperature = min(self.body_temperature + 0.02, MAX_TEMPERATURE)

        # Impact d'un abri sur la température corporelle et l'énergie
        if self.has_shelter:
            if self.body_temperature < MAX_TEMPERATURE:
                self.body_temperature = min(
                    self.body_temperature + 0.005, MAX_TEMPERATURE
                )

            # Récupération d'énergie pendant la nuit si dans un abri
            if game.time_of_day == TimeOfDay.NIGHT:
                self.energy = min(self.energy + 0.05, MAX_ENERGY)

        # Impact de la faim et de la soif sur la santé
        if self.hunger <= 0:
            self.health -= 0.1 * game.time_scale
            self.hunger = 0

        if self.thirst <= 0:
            self.health -= 0.2 * game.time_scale
            self.thirst = 0

        # Impact de la température corporelle sur la santé
        if abs(self.body_temperature - MAX_TEMPERATURE) > 2:
            self.health -= 0.05 * game.time_scale

        # Limites des statistiques
        self.hunger = max(0, min(self.hunger, MAX_HUNGER))
        self.thirst = max(0, min(self.thirst, MAX_THIRST))
        self.energy = max(0, min(self.energy, MAX_ENERGY))
        self.health = max(0, min(self.health, MAX_HEALTH))

    def eat(self, item_name):
        if not self.inventory.has_item(item_name):
            self.add_message(f"Vous n'avez pas de {item_name} dans votre inventaire.")
            return False

        item = next((i for i in Item.all_items if i.name == item_name), None)
        if not item or not item.is_food:
            self.add_message(f"{item_name} n'est pas comestible.")
            return False

        self.hunger += item.hunger_value
        self.thirst += item.thirst_value
        self.inventory.remove_item(item_name)

        self.add_message(f"Vous avez mangé {item_name}.")
        if item_name == "Viande crue":
            # Risque de maladie avec la viande crue
            if random.random() < 0.3:
                self.health -= 10
                self.add_message(
                    "Vous ne vous sentez pas bien après avoir mangé de la viande crue."
                )

        self.hunger = min(self.hunger, MAX_HUNGER)
        self.thirst = min(self.thirst, MAX_THIRST)
        return True

    def drink(self, item_name):
        if not self.inventory.has_item(item_name):
            self.add_message(f"Vous n'avez pas de {item_name} dans votre inventaire.")
            return False

        item = next((i for i in Item.all_items if i.name == item_name), None)
        if not item or not item.is_drinkable:
            self.add_message(f"{item_name} n'est pas buvable.")
            return False

        self.thirst += item.thirst_value
        self.inventory.remove_item(item_name)

        self.add_message(f"Vous avez bu {item_name}.")
        if item_name == "Eau de pluie" and random.random() < 0.2:
            # Risque de maladie avec l'eau non purifiée
            self.health -= 5
            self.add_message("Cette eau n'était peut-être pas assez propre...")

        self.thirst = min(self.thirst, MAX_THIRST)
        return True

    def rest(self, hours):
        if not self.has_shelter and random.random() < 0.5:
            # Risque en dormant sans abri
            self.add_message(
                "Vous avez été dérangé pendant votre sommeil et n'avez pas pu vous reposer correctement."
            )
            self.energy += hours * 5
        else:
            self.energy += hours * 10
            self.add_message(f"Vous vous êtes reposé pendant {hours} heures.")

        # Diminution de la faim et de la soif pendant le repos
        self.hunger -= hours * 1
        self.thirst -= hours * 1.5

        self.energy = min(self.energy, MAX_ENERGY)
        return True

    def build_shelter(self):
        required_materials = {"Bois": 5, "Corde": 2}

        # Vérification des matériaux
        for material, quantity in required_materials.items():
            if not self.inventory.has_item(material, quantity):
                self.add_message(
                    f"Vous avez besoin de {quantity} {material} pour construire un abri."
                )
                return False

        # Consommation des matériaux
        for material, quantity in required_materials.items():
            self.inventory.remove_item(material, quantity)

        self.has_shelter = True
        self.energy -= 20
        self.add_message("Vous avez construit un abri simple mais efficace!")
        return True

    def make_fire(self):
        required_materials = {"Bois": 3}

        # Vérification des matériaux
        for material, quantity in required_materials.items():
            if not self.inventory.has_item(material, quantity):
                self.add_message(
                    f"Vous avez besoin de {quantity} {material} pour faire un feu."
                )
                return False

        # Vérification du briquet
        has_lighter = self.inventory.has_item("Briquet")

        # Consommation des matériaux
        for material, quantity in required_materials.items():
            self.inventory.remove_item(material, quantity)

        # Chance de réussite
        success_chance = 0.9 if has_lighter else 0.5

        if random.random() < success_chance:
            self.has_fire = True
            self.fire_duration = 8  # Le feu dure 8 heures
            self.energy -= 10
            self.add_message("Vous avez réussi à allumer un feu!")
            return True
        else:
            self.add_message("Vous n'avez pas réussi à allumer le feu.")
            return False

    def cook(self, item_name):
        if not self.has_fire:
            self.add_message("Vous avez besoin d'un feu pour cuisiner.")
            return False

        if item_name == "Viande crue" and self.inventory.has_item(item_name):
            self.inventory.remove_item(item_name)
            self.inventory.add_item(
                next(i for i in Item.all_items if i.name == "Viande cuite")
            )
            self.add_message("Vous avez cuisiné de la viande crue en viande cuite.")

            # Amélioration de la compétence de cuisine
            self.skills["Cuisine"] += 0.1
            return True
        else:
            self.add_message(f"Vous ne pouvez pas cuisiner {item_name}.")
            return False

    def hunt(self, game):
        if self.energy < 20:
            self.add_message("Vous êtes trop fatigué pour chasser.")
            return False

        # Vérification d'une arme
        has_weapon = any(
            item_name
            for item_name in self.inventory.items
            if next((i for i in Item.all_items if i.name == item_name), None).is_weapon
        )

        success_chance = 0.3 + (0.1 * self.skills["Chasse"])
        if has_weapon:
            success_chance += 0.2

        if random.random() < success_chance:
            # Réussite de la chasse
            meat_qty = random.randint(1, 3)
            for _ in range(meat_qty):
                self.inventory.add_item(
                    next(i for i in Item.all_items if i.name == "Viande crue")
                )

            self.add_message(
                f"Chasse réussie! Vous avez obtenu {meat_qty} morceaux de viande crue."
            )

            # Amélioration de la compétence de chasse
            self.skills["Chasse"] += 0.2
        else:
            self.add_message("Vous n'avez rien trouvé à chasser.")

        self.energy -= 20
        self.hunger -= 5
        self.thirst -= 10
        return True

    def forage(self, game):
        if self.energy < 15:
            self.add_message("Vous êtes trop fatigué pour chercher des ressources.")
            return False

        # Recherche de ressources basée sur l'environnement actuel
        found_items = []

        # Chances de trouver des ressources
        if game.current_weather != Weather.STORMY:
            if random.random() < 0.7:
                wood_qty = random.randint(1, 3)
                for _ in range(wood_qty):
                    self.inventory.add_item(
                        next(i for i in Item.all_items if i.name == "Bois")
                    )
                found_items.append(f"{wood_qty} Bois")

            if random.random() < 0.5:
                stone_qty = random.randint(1, 2)
                for _ in range(stone_qty):
                    self.inventory.add_item(
                        next(i for i in Item.all_items if i.name == "Pierre")
                    )
                found_items.append(f"{stone_qty} Pierre")

            if random.random() < 0.3:
                self.inventory.add_item(
                    next(i for i in Item.all_items if i.name == "Corde")
                )
                found_items.append("1 Corde")

            if random.random() < 0.4:
                berry_qty = random.randint(1, 4)
                for _ in range(berry_qty):
                    self.inventory.add_item(
                        next(i for i in Item.all_items if i.name == "Baies")
                    )
                found_items.append(f"{berry_qty} Baies")

            # Collecte d'eau pendant la pluie
            if game.current_weather == Weather.RAINY and random.random() < 0.8:
                water_qty = random.randint(1, 2)
                for _ in range(water_qty):
                    self.inventory.add_item(
                        next(i for i in Item.all_items if i.name == "Eau de pluie")
                    )
                found_items.append(f"{water_qty} Eau de pluie")

        if found_items:
            self.add_message(f"Vous avez trouvé: {', '.join(found_items)}")
        else:
            self.add_message("Vous n'avez rien trouvé d'intéressant.")

        self.energy -= 15
        self.hunger -= 3
        self.thirst -= 7
        return True

    def craft(self, item_name):
        crafting_recipes = {
            "Couteau de fortune": {"Pierre": 1, "Bois": 1},
            "Lance en bois": {"Bois": 2, "Corde": 1},
            "Hache de pierre": {"Pierre": 2, "Bois": 1, "Corde": 1},
        }

        if item_name not in crafting_recipes:
            self.add_message(f"Vous ne savez pas fabriquer {item_name}.")
            return False

        required_materials = crafting_recipes[item_name]

        # Vérification des matériaux
        for material, quantity in required_materials.items():
            if not self.inventory.has_item(material, quantity):
                self.add_message(
                    f"Vous avez besoin de {quantity} {material} pour fabriquer {item_name}."
                )
                return False

        # Consommation des matériaux
        for material, quantity in required_materials.items():
            self.inventory.remove_item(material, quantity)

        # Ajout de l'objet fabriqué
        self.inventory.add_item(next(i for i in Item.all_items if i.name == item_name))

        self.add_message(f"Vous avez fabriqué {item_name}!")

        # Amélioration de la compétence de construction
        self.skills["Construction"] += 0.2
        self.energy -= 10
        return True

    def purify_water(self):
        if not self.has_fire:
            self.add_message("Vous avez besoin d'un feu pour purifier l'eau.")
            return False

        if not self.inventory.has_item("Eau de pluie"):
            self.add_message("Vous n'avez pas d'eau de pluie à purifier.")
            return False

        self.inventory.remove_item("Eau de pluie")
        self.inventory.add_item(
            next(i for i in Item.all_items if i.name == "Eau purifiée")
        )

        self.add_message("Vous avez purifié de l'eau de pluie en eau potable.")
        return True


# Interface utilisateur
class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        color=GRAY,
        hover_color=LIGHT_BLUE,
        text_color=BLACK,
        action=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.hovered = False

    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, 0, 5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, 5)

        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            if self.action:
                return self.action()
        return False


# Classe pour la gestion des popups
class Popup:
    def __init__(self, title, content, buttons=None):
        self.title = title
        self.content = content
        self.buttons = buttons if buttons else []
        self.active = True

        # Dimensionnement du popup
        self.width = 400
        self.height = 300
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if not self.active:
            return

        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Fond du popup
        pygame.draw.rect(screen, WHITE, self.rect, 0, 10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, 10)

        # Titre
        font_title = pygame.font.SysFont(None, 32)
        text_title = font_title.render(self.title, True, BLACK)
        screen.blit(text_title, (self.x + 20, self.y + 20))

        # Contenu
        font_content = pygame.font.SysFont(None, 24)
        lines = self.content.split("\n")
        for i, line in enumerate(lines):
            text_line = font_content.render(line, True, BLACK)
            screen.blit(text_line, (self.x + 20, self.y + 60 + i * 30))

        # Boutons
        for button in self.buttons:
            button.draw(screen)

    def update(self, mouse_pos):
        if not self.active:
            return

        for button in self.buttons:
            button.update(mouse_pos)

    def handle_event(self, event):
        if not self.active:
            return False

        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False


# Classe principale du jeu
class SurvivalGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Survie Réaliste - Jeu de Simulation")
        self.clock = pygame.time.Clock()
        self.player = None
        self.days_survived = 1
        self.time_of_day = TimeOfDay.MORNING
        self.current_weather = Weather.SUNNY
        self.time_scale = 0.1  # Facteur d'écoulement du temps
        self.running = True

        # Interface
        self.buttons = []
        self.active_popup = None
        self.inventory_visible = False
        self.crafting_visible = False

        # Images de fond selon le temps/jour
        self.background_images = {
            # Format: (TimeOfDay, Weather): image_path
            (TimeOfDay.MORNING, Weather.SUNNY): "bg_morning_sunny.png",
            (TimeOfDay.AFTERNOON, Weather.SUNNY): "bg_afternoon_sunny.png",
            (TimeOfDay.EVENING, Weather.SUNNY): "bg_evening_sunny.png",
            (TimeOfDay.NIGHT, Weather.SUNNY): "bg_night_sunny.png",
            # Etc. pour d'autres combinaisons
        }

        # Image par défaut
        self.default_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.default_bg.fill((100, 150, 200))  # Bleu ciel par défaut

        # Chargement des ressources
        self.initialize_resources()

        # Actions
        self.initialize_actions()

    def initialize_resources(self):
        # Charger les images (ou créer des placeholders)
        self.images = {
            "player": load_image("player.png"),
            "fire": load_image("fire.png"),
            "shelter": load_image("shelter.png"),
            # Charger les backgrounds ici s'ils existent
        }

    def toggle_inventory(self):
        self.inventory_visible = not self.inventory_visible
        self.crafting_visible = False
        return True

    def toggle_crafting(self):
        self.crafting_visible = not self.crafting_visible
        self.inventory_visible = False
        return True

    def show_consume_popup(self):
        content = "Que voulez-vous consommer?"
        buttons = []

        food_items = [
            name
            for name, qty in self.player.inventory.items.items()
            if next((i for i in Item.all_items if i.name == name), None).is_food
        ]

        drink_items = [
            name
            for name, qty in self.player.inventory.items.items()
            if next((i for i in Item.all_items if i.name == name), None).is_drinkable
        ]

        y_offset = 0
        for i, item in enumerate(food_items):
            y = self.screen.get_height() // 2 - 50 + y_offset
            buttons.append(
                Button(
                    self.screen.get_width() // 2 - 180,
                    y,
                    150,
                    30,
                    f"Manger {item}",
                    action=lambda i=item: self.consume_item("eat", i),
                )
            )
            y_offset += 40

        y_offset = 0
        for i, item in enumerate(drink_items):
            y = self.screen.get_height() // 2 - 50 + y_offset
            buttons.append(
                Button(
                    self.screen.get_width() // 2 + 30,
                    y,
                    150,
                    30,
                    f"Boire {item}",
                    action=lambda i=item: self.consume_item("drink", i),
                )
            )
            y_offset += 40

        # Bouton Annuler
        buttons.append(
            Button(
                self.screen.get_width() // 2 - 40,
                self.screen.get_height() // 2 + 100,
                80,
                30,
                "Annuler",
                action=self.close_popup,
            )
        )

        self.active_popup = Popup("Consommer", content, buttons)
        return True

    def perform_action(self, action):
        if action == "hunt":
            self.player.hunt(self)
        elif action == "forage":
            self.player.forage(self)
        elif action == "fire":
            if self.player.has_fire:
                self.player.add_message("Vous avez déjà un feu allumé.")
            else:
                self.player.make_fire()
        elif action == "shelter":
            if self.player.has_shelter:
                self.player.add_message("Vous avez déjà construit un abri.")
            else:
                self.player.build_shelter()
        return True

    def show_rest_popup(self):
        content = "Combien d'heures voulez-vous vous reposer?"
        buttons = []

        for hours in [2, 4, 8]:
            buttons.append(
                Button(
                    self.screen.get_width() // 2 - 40,
                    self.screen.get_height() // 2 - 30 + hours * 10,
                    80,
                    30,
                    f"{hours}h",
                    action=lambda h=hours: self.rest(h),
                )
            )

        # Bouton Annuler
        buttons.append(
            Button(
                self.screen.get_width() // 2 - 40,
                self.screen.get_height() // 2 + 70,
                80,
                30,
                "Annuler",
                action=self.close_popup,
            )
        )

        self.active_popup = Popup("Repos", content, buttons)
        return True

    def initialize_actions(self):
        button_width = 130
        button_height = 40
        button_margin = 10
        start_x = 20
        start_y = SCREEN_HEIGHT - 50

        actions = [
            {"text": "Inventaire", "action": self.toggle_inventory},
            {"text": "Fabriquer", "action": self.toggle_crafting},
            {"text": "Manger/Boire", "action": self.show_consume_popup},
            {"text": "Chasser", "action": lambda: self.perform_action("hunt")},
            {"text": "Cueillette", "action": lambda: self.perform_action("forage")},
            {"text": "Feu", "action": lambda: self.perform_action("fire")},
            {"text": "Abri", "action": lambda: self.perform_action("shelter")},
            {"text": "Repos", "action": self.show_rest_popup},
        ]

        for i, action in enumerate(actions):
            x = start_x + (button_width + button_margin) * (i % 4)
            y = start_y - (button_height + button_margin) * (i // 4)
            self.buttons.append(
                Button(
                    x,
                    y,
                    button_width,
                    button_height,
                    action["text"],
                    action=action["action"],
                )
            )

    def initialize(self):
        # Créer le joueur
        self.player = Player("Survivant")

        # Initialisation des objets du jeu
        Item.initialize_items()

        # Objets de départ
        self.player.inventory.add_item(
            next(i for i in Item.all_items if i.name == "Couteau de fortune")
        )
        self.player.inventory.add_item(
            next(i for i in Item.all_items if i.name == "Baies"), 2
        )
        self.player.inventory.add_item(
            next(i for i in Item.all_items if i.name == "Eau de pluie")
        )

        # Message de bienvenue
        self.player.add_message(
            "Vous vous réveillez dans une forêt inconnue. Vous devez survivre."
        )

    def update_game_state(self):
        # Mise à jour du temps de jeu
        if random.random() < 0.05 * self.time_scale:
            # Changement de la période de la journée
            times = list(TimeOfDay)
            current_index = times.index(self.time_of_day)
            self.time_of_day = times[(current_index + 1) % len(times)]

            if self.time_of_day == TimeOfDay.MORNING:
                # Nouvelle journée
                self.days_survived += 1
                self.player.add_message(f"Jour {self.days_survived}")

                # Chance de changement météo
                if random.random() < 0.3:
                    weathers = list(Weather)
                    self.current_weather = random.choice(weathers)
                    self.player.add_message(
                        f"Le temps change: {self.current_weather.name}"
                    )

        # Mise à jour du feu
        if self.player.has_fire:
            self.player.fire_duration -= 0.1 * self.time_scale
            if self.player.fire_duration <= 0:
                self.player.has_fire = False
                self.player.fire_duration = 0
                self.player.add_message("Le feu s'est éteint.")

        # Mise à jour des statistiques du joueur
        self.player.update_stats(self)

        # Vérification de fin de jeu
        if self.player.health <= 0:
            self.show_game_over_popup()

    def show_game_over_popup(self):
        content = f"Vous n'avez pas survécu.\nJours de survie: {self.days_survived}\n\nVoulez-vous recommencer?"
        buttons = [
            Button(
                self.screen.get_width() // 2 - 100,
                self.screen.get_height() // 2 + 50,
                80,
                40,
                "Oui",
                action=self.restart_game,
            ),
            Button(
                self.screen.get_width() // 2 + 20,
                self.screen.get_height() // 2 + 50,
                80,
                40,
                "Non",
                action=self.quit_game,
            ),
        ]
        self.active_popup = Popup("Fin de partie", content, buttons)

    def restart_game(self):
        self.active_popup = None
        self.initialize()
        return True

    def quit_game(self):
        self.running = False
        return True

    def consume_item(self, action_type, item_name):
        if action_type == "eat":
            self.player.eat(item_name)
        elif action_type == "drink":
            self.player.drink(item_name)

        self.active_popup = None
        return True

    def rest(self, hours):
        self.player.rest(hours)

        # Accélération du temps
        for _ in range(int(hours * 10)):
            self.update_game_state()

        self.active_popup = None
        return True

    def close_popup(self):
        self.active_popup = None
        return True

    def draw_status_bars(self):
        # Barres de statut pour santé, faim, soif, énergie et température
        bar_width = 150
        bar_height = 20
        bar_margin = 10
        start_x = 20
        start_y = 20

        stats = [
            {
                "name": "Santé",
                "value": self.player.health,
                "max": MAX_HEALTH,
                "color": RED,
            },
            {
                "name": "Faim",
                "value": self.player.hunger,
                "max": MAX_HUNGER,
                "color": GREEN,
            },
            {
                "name": "Soif",
                "value": self.player.thirst,
                "max": MAX_THIRST,
                "color": BLUE,
            },
            {
                "name": "Énergie",
                "value": self.player.energy,
                "max": MAX_ENERGY,
                "color": YELLOW,
            },
        ]

        font = pygame.font.SysFont(None, 24)

        for i, stat in enumerate(stats):
            # Cadre
            bar_rect = pygame.Rect(
                start_x, start_y + (bar_height + bar_margin) * i, bar_width, bar_height
            )
            pygame.draw.rect(self.screen, BLACK, bar_rect, 2)

            # Remplissage
            fill_width = int((stat["value"] / stat["max"]) * (bar_width - 4))
            fill_rect = pygame.Rect(
                start_x + 2,
                start_y + 2 + (bar_height + bar_margin) * i,
                fill_width,
                bar_height - 4,
            )
            pygame.draw.rect(self.screen, stat["color"], fill_rect)

            # Texte
            text = font.render(
                f"{stat['name']}: {int(stat['value'])}/{stat['max']}", True, BLACK
            )
            self.screen.blit(
                text,
                (start_x + bar_width + 10, start_y + (bar_height + bar_margin) * i),
            )

        # Température
        temp_y = start_y + (bar_height + bar_margin) * len(stats)
        temp_text = font.render(
            f"Température: {self.player.body_temperature:.1f}°C", True, BLACK
        )
        self.screen.blit(temp_text, (start_x, temp_y))

        # Jour et temps
        day_text = font.render(
            f"Jour: {self.days_survived} - {self.time_of_day.name}", True, BLACK
        )
        self.screen.blit(day_text, (start_x, temp_y + 30))

        # Météo
        weather_text = font.render(f"Météo: {self.current_weather.name}", True, BLACK)
        self.screen.blit(weather_text, (start_x, temp_y + 60))

    def draw_message_log(self):
        font = pygame.font.SysFont(None, 20)
        log_width = 300
        log_height = 150
        log_x = SCREEN_WIDTH - log_width - 20
        log_y = 20

        # Fond semi-transparent
        log_surface = pygame.Surface((log_width, log_height), pygame.SRCALPHA)
        log_surface.fill((0, 0, 0, 128))
        self.screen.blit(log_surface, (log_x, log_y))

        # Bordure
        pygame.draw.rect(self.screen, WHITE, (log_x, log_y, log_width, log_height), 2)

        # Messages
        for i, message in enumerate(self.player.message_log):
            if i >= 8:  # Limiter à 8 messages affichés
                break
            text = font.render(message, True, WHITE)
            self.screen.blit(text, (log_x + 10, log_y + 10 + i * 20))

    def draw_inventory(self):
        if not self.inventory_visible:
            return

        inventory_width = 400
        inventory_height = 400
        inventory_x = (SCREEN_WIDTH - inventory_width) // 2
        inventory_y = (SCREEN_HEIGHT - inventory_height) // 2

        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # Fond de l'inventaire
        inventory_surface = pygame.Surface((inventory_width, inventory_height))
        inventory_surface.fill(WHITE)
        self.screen.blit(inventory_surface, (inventory_x, inventory_y))

        # Bordure
        pygame.draw.rect(
            self.screen,
            BLACK,
            (inventory_x, inventory_y, inventory_width, inventory_height),
            2,
        )

        # Titre
        font_title = pygame.font.SysFont(None, 32)
        title_text = font_title.render(
            f"Inventaire ({self.player.inventory.current_weight:.1f}/{self.player.inventory.max_weight} kg)",
            True,
            BLACK,
        )
        self.screen.blit(title_text, (inventory_x + 10, inventory_y + 10))

        # Items
        font_items = pygame.font.SysFont(None, 24)
        item_y = inventory_y + 50
        for item_name, quantity in self.player.inventory.items.items():
            item = next((i for i in Item.all_items if i.name == item_name), None)
            if item:
                item_text = font_items.render(
                    f"{item_name} x{quantity} ({item.weight * quantity:.1f} kg)",
                    True,
                    BLACK,
                )
                if item.icon:
                    self.screen.blit(item.icon, (inventory_x + 10, item_y))
                    self.screen.blit(item_text, (inventory_x + 80, item_y + 10))
                else:
                    self.screen.blit(item_text, (inventory_x + 10, item_y))

                item_y += 40

        # Bouton Fermer
        close_button = Button(
            inventory_x + inventory_width - 90,
            inventory_y + inventory_height - 40,
            80,
            30,
            "Fermer",
            action=self.toggle_inventory,
        )
        close_button.draw(self.screen)

    def draw_crafting(self):
        if not self.crafting_visible:
            return

        crafting_width = 500
        crafting_height = 400
        crafting_x = (SCREEN_WIDTH - crafting_width) // 2
        crafting_y = (SCREEN_HEIGHT - crafting_height) // 2

        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # Fond du crafting
        crafting_surface = pygame.Surface((crafting_width, crafting_height))
        crafting_surface.fill(WHITE)
        self.screen.blit(crafting_surface, (crafting_x, crafting_y))

        # Bordure
        pygame.draw.rect(
            self.screen,
            BLACK,
            (crafting_x, crafting_y, crafting_width, crafting_height),
            2,
        )

        # Titre
        font_title = pygame.font.SysFont(None, 32)
        title_text = font_title.render("Fabrication", True, BLACK)
        self.screen.blit(title_text, (crafting_x + 10, crafting_y + 10))

        # Recettes
        font_items = pygame.font.SysFont(None, 24)
        recipes = [
            {"name": "Couteau de fortune", "materials": {"Pierre": 1, "Bois": 1}},
            {"name": "Lance en bois", "materials": {"Bois": 2, "Corde": 1}},
            {
                "name": "Hache de pierre",
                "materials": {"Pierre": 2, "Bois": 1, "Corde": 1},
            },
            {"name": "Purifier l'eau", "special": "purify_water"},
        ]

        item_y = crafting_y + 50
        buttons = []

        for recipe in recipes:
            if "special" in recipe:
                # Action spéciale
                text = "Purifier l'eau (Eau de pluie + Feu)"
                can_craft = self.player.has_fire and self.player.inventory.has_item(
                    "Eau de pluie"
                )
            else:
                # Recette standard
                text = f"{recipe['name']} - Matériaux: " + ", ".join(
                    [f"{qty} {mat}" for mat, qty in recipe["materials"].items()]
                )
                can_craft = all(
                    self.player.inventory.has_item(mat, qty)
                    for mat, qty in recipe["materials"].items()
                )

            item_text = font_items.render(text, True, BLACK)
            self.screen.blit(item_text, (crafting_x + 10, item_y))

            # Bouton Fabriquer
            button_color = GREEN if can_craft else GRAY
            if "special" in recipe:
                craft_action = lambda r=recipe["special"]: self.special_craft(r)
            else:
                craft_action = lambda r=recipe["name"]: self.craft_item(r)

            craft_button = Button(
                crafting_x + crafting_width - 110,
                item_y,
                100,
                30,
                "Fabriquer",
                color=button_color,
                action=craft_action,
            )
            craft_button.draw(self.screen)
            buttons.append(craft_button)

            item_y += 60

        # Bouton Fermer
        close_button = Button(
            crafting_x + crafting_width - 90,
            crafting_y + crafting_height - 40,
            80,
            30,
            "Fermer",
            action=self.toggle_crafting,
        )
        close_button.draw(self.screen)
        buttons.append(close_button)

        # Mise à jour et gestion des boutons
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update(mouse_pos)

    def craft_item(self, item_name):
        self.player.craft(item_name)
        return True

    def special_craft(self, action):
        if action == "purify_water":
            self.player.purify_water()
        return True

    def draw(self):
        # Fond d'écran selon la météo et l'heure
        background_key = (self.time_of_day, self.current_weather)
        if background_key in self.background_images:
            bg_path = self.background_images[background_key]
            if os.path.exists(bg_path):
                bg_image = load_image(bg_path, scale=1.0)
                self.screen.blit(bg_image, (0, 0))
            else:
                self.screen.blit(self.default_bg, (0, 0))
        else:
            self.screen.blit(self.default_bg, (0, 0))

        # Dessin des éléments de jeu
        if self.player.has_shelter:
            self.screen.blit(
                self.images["shelter"], (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
            )

        if self.player.has_fire:
            self.screen.blit(
                self.images["fire"], (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 + 30)
            )

        # Joueur
        self.screen.blit(self.images["player"], (self.player.x, self.player.y))

        # Interface utilisateur
        self.draw_status_bars()
        self.draw_message_log()

        # Boutons d'action
        for button in self.buttons:
            button.draw(self.screen)

        # Inventaire et crafting (si visible)
        self.draw_inventory()
        self.draw_crafting()

        # Popup (si actif)
        if self.active_popup:
            self.active_popup.draw(self.screen)

        # Mise à jour de l'écran
        pygame.display.flip()

    def run(self):
        self.initialize()

        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Gérer les clics sur les boutons
                if self.active_popup:
                    self.active_popup.handle_event(event)
                elif self.inventory_visible:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Bouton pour fermer l'inventaire
                        inventory_width = 400
                        inventory_height = 400
                        inventory_x = (SCREEN_WIDTH - inventory_width) // 2
                        inventory_y = (SCREEN_HEIGHT - inventory_height) // 2
                        close_button_rect = pygame.Rect(
                            inventory_x + inventory_width - 90,
                            inventory_y + inventory_height - 40,
                            80,
                            30,
                        )
                        if close_button_rect.collidepoint(event.pos):
                            self.inventory_visible = False
                elif self.crafting_visible:
                    # Gestion des boutons de crafting
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        crafting_width = 500
                        crafting_height = 400
                        crafting_x = (SCREEN_WIDTH - crafting_width) // 2
                        crafting_y = (SCREEN_HEIGHT - crafting_height) // 2

                        # Vérifier les boutons de crafting
                        recipes = [
                            {
                                "name": "Couteau de fortune",
                                "materials": {"Pierre": 1, "Bois": 1},
                            },
                            {
                                "name": "Lance en bois",
                                "materials": {"Bois": 2, "Corde": 1},
                            },
                            {
                                "name": "Hache de pierre",
                                "materials": {"Pierre": 2, "Bois": 1, "Corde": 1},
                            },
                            {"name": "Purifier l'eau", "special": "purify_water"},
                        ]

                        for i, recipe in enumerate(recipes):
                            craft_button_rect = pygame.Rect(
                                crafting_x + crafting_width - 110,
                                crafting_y + 50 + i * 60,
                                100,
                                30,
                            )
                            if craft_button_rect.collidepoint(event.pos):
                                if "special" in recipe:
                                    self.special_craft(recipe["special"])
                                else:
                                    self.craft_item(recipe["name"])

                        # Bouton pour fermer le crafting
                        close_button_rect = pygame.Rect(
                            crafting_x + crafting_width - 90,
                            crafting_y + crafting_height - 40,
                            80,
                            30,
                        )
                        if close_button_rect.collidepoint(event.pos):
                            self.crafting_visible = False
                else:
                    for button in self.buttons:
                        if (
                            event.type == pygame.MOUSEBUTTONDOWN
                            and button.rect.collidepoint(mouse_pos)
                        ):
                            button.action()

            # Mise à jour des boutons
            for button in self.buttons:
                button.update(mouse_pos)

            # Mise à jour de l'état du jeu
            self.update_game_state()

            # Dessin
            self.draw()

            # Contrôle de la fréquence d'images
            self.clock.tick(FPS)

        pygame.quit()


# Point d'entrée du programme
if __name__ == "__main__":
    game = SurvivalGame()
    game.run()
