# -*- coding: utf-8 -*-
from modules import *

class Player(Creature):
  """ Description of player """
  def __init__(self, game, position = (0, 0)):
    super(Player, self).__init__(game, position, 'PLAYER')
    self.state = 'ALIVE'
    self.take_turn = None
    self.is_fov_recompute = True

  ### ACTIONS #################################################################
  def move_or_attack(self, dx, dy):
    if self.game.state == 'PLAYING':
      object = self.move(dx, dy)
      if not object:
        self.is_fov_recompute = True
        self.show_objects_under_player()
      elif isinstance(object, Creature):
        self.attack(object)

  def pick_up(self):
    items = Item.get_by_position(self.x, self.y)
    if len(items) == 0:
      Text.event_nothing_to_pick_up(self.game.panel)
      return None

    index = 0
    if len(items) > 1:
      index = self.game.menu.show(Text.inventory_pick_up(), 
        [item.name for item in items])
    if index != None:
      item = items[index]
      if len(self.inventory) >= INVETORY_LIMIT:
        if self == self.game.player: Text.event_inventory_full(self.game.player, item.name)
        return
      elif self.inventory_weight() + item.weight <= self.stats['SP'].base_value:
        Item.list.remove(item)
        self.inventory.append(item)
        self.stats['SP'].value = self.inventory_weight()
        if self == self.game.player: Text.event_pick_up_item(item.name)
      else:
        if self == self.game.player: Text.event_overload(self.game.panel)
        return None

  def use(self, action = 'GENERAL'):
    item = self.get_item_from_inventory(Text.inventory_use(), action)
    if item:
      Action.apply(item, self, action)
      self.stats['SP'].value = self.inventory_weight()

  def death(self):
    your_corpse = Item((self.x, self.y), 'CORPSE')
    your_corpse.name = Text.corpse_name(self.name)
    #Why? I don't know, lol
    your_corpse.weight = self.weight
    Creature.list.remove(self)
    self.state = 'DEAD'
    self.drop_all()
    Text.event_death(self.name)
    #del self

  def drop(self, item=None):
    if not item:
      item = self.get_item_from_inventory(Text.inventory_drop())
    if item:
      self.inventory.remove(item)
      item.x, item.y = self.x, self.y
      Item.list.append(item)
      Text.event_drop(self.name, item.name)

  def action_on_target(self, effect, params):
    self.game.aim.activate(self, effect, params)
  #############################################################################

  def get_item_from_inventory(self, header, action = 'GENERAL'):
    inventory_hash = {}
    filtered = self.inventory[:]
    options = []

    if len(self.inventory) == 0:
      self.game.menu.show(header, [Text.inventory_empty()])
      return None
    else:
      if action != 'GENERAL':
        filtered =  [item for item in self.inventory if action in item.actions][:]
      for item in filtered:
        if item.name in inventory_hash.keys():
          inventory_hash[item.name] += 1
        else:
          inventory_hash[item.name] = 1

      for item in inventory_hash:
        if inventory_hash[item] > 1:
          options.append(item + ' x' + str(inventory_hash[item]))
        else: options.append(item)

      index = self.game.menu.show(header, sorted(options))
      if index != None:
        name = sorted(inventory_hash.keys())[index]
        for item in self.inventory:
          if item.name == name: return item
      else: return None

  def show_objects_under_player(self):
    names = self.game.map.get_names_at_position(self.x, self.y, self)
    Text.event_observation(names)


