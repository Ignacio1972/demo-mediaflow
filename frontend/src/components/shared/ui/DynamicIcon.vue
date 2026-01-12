<script setup lang="ts">
import { computed, shallowRef, watch, type Component } from 'vue'

// Lucide icons (for icons not available in Heroicons)
import {
  Rabbit as RabbitIcon,
  Snowflake as SnowflakeIcon,
  PartyPopper as PartyPopperIcon,
  Egg as EggIcon,
  Flag as FlagIcon,
  Flower2 as Flower2Icon,
  Shirt as ShirtIcon,
  Baby as BabyIcon,
  IceCreamCone as IceCreamConeIcon,
  Bug as BugIcon,
  Save as SaveIcon,
  Laptop as LaptopIcon,
  Glasses as GlassesIcon,
} from 'lucide-vue-next'

// Heroicons
import {
  // Commerce & Shopping
  ShoppingBagIcon,
  ShoppingCartIcon,
  GiftIcon,
  TagIcon,
  CreditCardIcon,
  BanknotesIcon,
  // Events & Celebration
  SparklesIcon,
  StarIcon,
  HeartIcon,
  FireIcon,
  TrophyIcon,
  CakeIcon,
  // Communication
  MegaphoneIcon,
  ChatBubbleLeftIcon,
  BellIcon,
  EnvelopeIcon,
  // Seasons & Weather
  SunIcon,
  MoonIcon,
  CloudIcon,
  // Media & Content
  FolderIcon,
  DocumentTextIcon,
  PhotoIcon,
  MusicalNoteIcon,
  FilmIcon,
  MicrophoneIcon,
  // Actions & States
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  // Navigation & UI
  HomeIcon,
  CubeIcon,
  RocketLaunchIcon,
  LightBulbIcon,
  WrenchIcon,
  CalendarIcon,
  ClockIcon,
  MapPinIcon,
  UserGroupIcon,
  AcademicCapIcon,
  BookOpenIcon,
  GlobeAltIcon,
  TruckIcon,
  BuildingStorefrontIcon,
  TicketIcon,
  PuzzlePieceIcon,
  PhoneIcon,
  UsersIcon,
} from '@heroicons/vue/24/outline'

// Icon map: name -> component
const iconMap: Record<string, Component> = {
  // Commerce
  ShoppingBag: ShoppingBagIcon,
  ShoppingCart: ShoppingCartIcon,
  Gift: GiftIcon,
  Tag: TagIcon,
  CreditCard: CreditCardIcon,
  Banknotes: BanknotesIcon,
  // Events
  Sparkles: SparklesIcon,
  Star: StarIcon,
  Heart: HeartIcon,
  Fire: FireIcon,
  Trophy: TrophyIcon,
  Cake: CakeIcon,
  // Communication
  Megaphone: MegaphoneIcon,
  ChatBubble: ChatBubbleLeftIcon,
  Bell: BellIcon,
  Envelope: EnvelopeIcon,
  // Seasons
  Sun: SunIcon,
  Moon: MoonIcon,
  Cloud: CloudIcon,
  // Media
  Folder: FolderIcon,
  Document: DocumentTextIcon,
  Photo: PhotoIcon,
  Music: MusicalNoteIcon,
  Film: FilmIcon,
  Microphone: MicrophoneIcon,
  // Actions
  CheckCircle: CheckCircleIcon,
  ExclamationCircle: ExclamationCircleIcon,
  InfoCircle: InformationCircleIcon,
  // UI
  Home: HomeIcon,
  Cube: CubeIcon,
  Rocket: RocketLaunchIcon,
  LightBulb: LightBulbIcon,
  Wrench: WrenchIcon,
  Calendar: CalendarIcon,
  Clock: ClockIcon,
  MapPin: MapPinIcon,
  UserGroup: UserGroupIcon,
  AcademicCap: AcademicCapIcon,
  BookOpen: BookOpenIcon,
  Globe: GlobeAltIcon,
  Truck: TruckIcon,
  Store: BuildingStorefrontIcon,
  Ticket: TicketIcon,
  Puzzle: PuzzlePieceIcon,
  Phone: PhoneIcon,
  Users: UsersIcon,
  // Lucide icons (stroke-width will be set to 1.5 to match Heroicons)
  Rabbit: RabbitIcon,
  Snowflake: SnowflakeIcon,
  PartyPopper: PartyPopperIcon,
  Egg: EggIcon,
  Flag: FlagIcon,
  Flower2: Flower2Icon,
  Shirt: ShirtIcon,
  Baby: BabyIcon,
  IceCreamCone: IceCreamConeIcon,
  Bug: BugIcon,
  Save: SaveIcon,
  Laptop: LaptopIcon,
  Glasses: GlassesIcon,
}

// Set of Lucide icon names (need stroke-width adjustment)
const lucideIcons = new Set([
  'Rabbit', 'Snowflake', 'PartyPopper', 'Egg',
  'Flag', 'Flower2', 'Shirt', 'Baby', 'IceCreamCone',
  'Bug', 'Save', 'Laptop', 'Glasses'
])

interface Props {
  name: string | null | undefined
  fallback?: string
}

const props = withDefaults(defineProps<Props>(), {
  fallback: 'Folder'
})

// Detect if name is an emoji (unicode character) vs icon name
function isEmoji(str: string): boolean {
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]/u
  return emojiRegex.test(str)
}

// Resolved icon component
const iconComponent = shallowRef<Component | null>(null)
const showEmoji = shallowRef(false)
const emojiValue = shallowRef('')
const isLucideIcon = shallowRef(false)

// Resolve icon based on name
watch(
  () => props.name,
  (newName) => {
    if (!newName) {
      // No name provided, use fallback icon
      iconComponent.value = iconMap[props.fallback] || FolderIcon
      showEmoji.value = false
      isLucideIcon.value = lucideIcons.has(props.fallback)
      return
    }

    // Check if it's an emoji (backwards compatibility)
    if (isEmoji(newName)) {
      showEmoji.value = true
      emojiValue.value = newName
      iconComponent.value = null
      isLucideIcon.value = false
      return
    }

    // Try to find icon in map
    const icon = iconMap[newName]
    if (icon) {
      iconComponent.value = icon
      showEmoji.value = false
      isLucideIcon.value = lucideIcons.has(newName)
    } else {
      // Unknown icon name, use fallback
      iconComponent.value = iconMap[props.fallback] || FolderIcon
      showEmoji.value = false
      isLucideIcon.value = lucideIcons.has(props.fallback)
    }
  },
  { immediate: true }
)
</script>

<template>
  <span v-if="showEmoji">{{ emojiValue }}</span>
  <component
    v-else-if="iconComponent"
    :is="iconComponent"
    :stroke-width="isLucideIcon ? 1.5 : undefined"
  />
</template>
