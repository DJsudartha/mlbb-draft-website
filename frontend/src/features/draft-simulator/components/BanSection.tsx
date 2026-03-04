import { X } from 'lucide-react';
import type { Hero } from '../types/draft';

interface BanSectionProps {
  bans: Hero[];
  team: 'blue' | 'red';
  currentBanIndex?: number;
}

export function BanSection({ bans, team, currentBanIndex }: BanSectionProps) {
  const emptySlots = Array(5 - bans.length).fill(null);
  const borderColor = team === 'blue' ? 'border-blue-500/50' : 'border-red-500/50';
  const highlightColor = team === 'blue' ? 'border-blue-400 shadow-blue-400/50' : 'border-red-400 shadow-red-400/50';

  return (
    <div>
      <h3 className="mb-3 text-sm text-gray-400">Bans</h3>
      <div className="flex gap-3 justify-center">
        {bans.map((hero, index) => (
          <div 
            key={index}
            className={`relative w-14 h-14 rounded-full border-2 ${borderColor} bg-black/60 overflow-hidden`}
          >
            <img 
              src={hero.image} 
              alt={hero.name}
              className="w-full h-full object-cover opacity-50"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <X className="w-6 h-6 text-red-500" strokeWidth={3} />
            </div>
          </div>
        ))}
        {emptySlots.map((_, index) => {
          const slotIndex = bans.length + index;
          const isActive = currentBanIndex === slotIndex;
          
          return (
            <div 
              key={`empty-${index}`}
              className={`w-14 h-14 rounded-full border-2 ${
                isActive 
                  ? `${highlightColor} shadow-lg animate-pulse` 
                  : `border-dashed ${borderColor} bg-black/30`
              } ${!isActive && 'bg-black/30'} flex items-center justify-center`}
            >
              <X className="w-4 h-4 text-gray-600" />
            </div>
          );
        })}
      </div>
    </div>
  );
}