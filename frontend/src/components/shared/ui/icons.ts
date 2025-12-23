// Available icons for the icon selector system
// Maps friendly names to Heroicon component names

export const iconCategories: Record<string, string[]> = {
  'Campañas': ['Flag', 'Flower2', 'Shirt', 'Baby', 'Rabbit', 'Egg', 'Snowflake', 'IceCreamCone', 'PartyPopper'],
  'Comercio': ['ShoppingBag', 'ShoppingCart', 'Gift', 'Tag', 'CreditCard', 'Banknotes', 'Store', 'Ticket'],
  'Eventos': ['Sparkles', 'Star', 'Heart', 'Fire', 'Trophy', 'Cake', 'Rocket'],
  'Temporadas': ['Sun', 'Moon', 'Cloud', 'Glasses'],
  'Comunicacion': ['Megaphone', 'ChatBubble', 'Bell', 'Envelope', 'Microphone'],
  'Tiempo': ['Calendar', 'Clock'],
  'Contenido': ['Folder', 'Document', 'Photo', 'Music', 'Film', 'BookOpen', 'Save'],
  'Tech': ['Laptop', 'Bug'],
  'General': ['Home', 'Cube', 'LightBulb', 'Wrench', 'MapPin', 'UserGroup', 'AcademicCap', 'Globe', 'Truck', 'Puzzle'],
}

// Flat list of all available icon names
export const availableIcons = Object.values(iconCategories).flat()
