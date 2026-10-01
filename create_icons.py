"""
Generates clean SVG icons in assets/icons/ for use throughout the dashboard.
Completely eliminates emoji usage in favor of sharp, official vector icons.
"""
import os

ICONS = {
    'users.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
    
    'house.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>',
    
    'family.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M12 3L2 12h3v8h14v-8h3L12 3zm0 4.5c1.38 0 2.5 1.12 2.5 2.5s-1.12 2.5-2.5 2.5-2.5-1.12-2.5-2.5 1.12-2.5 2.5-2.5zm4 10.5H8v-1.5c0-1.33 2.67-2 4-2s4 .67 4 2v1.5z"/></svg>',
    
    'building.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/></svg>',
    
    'chart.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z"/><path d="M4 19h16v2H4z"/></svg>',
    
    'map.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/></svg>',
    
    'lightbulb.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-1.3l-.85-.6C7.8 13.16 7 11.42 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 2.42-.8 4.16-2.15 5.1z"/></svg>',
    
    'trending.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>',
    
    'filter.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/></svg>',
    
    'info.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',

    # Blue square versions for quick insights
    'insight_users.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
    'insight_house.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>',
    'insight_building.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/></svg>',
    'insight_trend.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0284c7"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>'
}

def create_all_icons():
    os.makedirs('assets/icons', exist_ok=True)
    for fname, content in ICONS.items():
        path = os.path.join('assets/icons', fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    print(f"Generated {len(ICONS)} SVG icons in assets/icons/")

if __name__ == '__main__':
    create_all_icons()
