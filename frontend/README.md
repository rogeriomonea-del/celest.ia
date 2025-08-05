# Celest.ia Frontend

Modern React-based dashboard for the Celest.ia flight search and analysis platform.

## Features

- 🎨 **Modern UI/UX**: Sleek, responsive design with dark theme and glassmorphism effects
- ✈️ **Flight Search**: Comprehensive search interface with multiple passenger types
- 📊 **Price Analytics**: Interactive charts showing price trends and AI insights
- 💳 **Miles Analysis**: Dedicated analysis for airline loyalty programs
- 📱 **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- 🔄 **Real-time Updates**: Live data integration with backend API

## Technology Stack

- **React 18**: Modern React with hooks and functional components
- **Vite**: Fast build tool and development server
- **Recharts**: Powerful charting library for data visualization
- **CSS3**: Custom CSS with CSS variables and modern features
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── charts/
│   │   │   ├── MilesChart.jsx      # Miles value trends
│   │   │   └── PriceChart.jsx      # Price analytics
│   │   ├── layout/
│   │   │   └── Dashboard.jsx       # Main dashboard layout
│   │   └── search/
│   │       └── FlightSearch.jsx    # Flight search interface
│   ├── services/
│   │   └── api.js                  # API service layer
│   ├── styles/
│   │   ├── globals.css             # Global styles and variables
│   │   ├── App.css                 # App component styles
│   │   ├── Dashboard.css           # Dashboard styles
│   │   ├── FlightSearch.css        # Search form styles
│   │   └── PriceChart.css          # Chart component styles
│   ├── App.jsx                     # Main application component
│   └── main.jsx                    # Application entry point
├── package.json
└── vite.config.js
```

## Component Architecture

### App.jsx
- Main application container
- Tab navigation system
- Global state management
- Theme and layout coordination

### Dashboard
- Overview statistics cards
- Recent searches display
- Activity feed
- Quick actions panel

### FlightSearch
- Multi-step search form
- Passenger type selection
- Route and date inputs
- Real-time validation
- Loading and error states

### PriceChart
- Interactive price trend visualization
- AI-generated insights
- Multiple view modes (prices/miles)
- Responsive chart container
- Custom tooltips and legends

### MilesChart
- Miles value comparison across airlines
- Historical trends analysis
- Best value recommendations
- Airline-specific insights

## Design System

### Color Palette
- **Primary**: Purple gradient (#8b5cf6 to #6366f1)
- **Secondary**: Cyan (#06b6d4)
- **Accent**: Amber (#f59e0b)
- **Success**: Emerald (#10b981)
- **Background**: Dark slate with transparency

### Typography
- **Font Family**: Inter, system fonts
- **Headings**: 600-700 weight with gradient text
- **Body**: 400-500 weight with proper contrast
- **UI Elements**: Uppercase labels with letter spacing

### Components
- **Glass Effect**: Backdrop blur with transparency
- **Gradients**: CSS gradients for visual hierarchy
- **Shadows**: Layered shadows for depth
- **Animations**: Smooth transitions and micro-interactions
- **Responsive**: Mobile-first breakpoints

## Development

### Prerequisites
- Node.js 16+
- npm or yarn

### Setup
```bash
cd frontend
npm install
npm run dev
```

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### API Integration
The frontend connects to the backend API for:
- Flight search requests
- Price trend data
- AI analysis results
- User preferences
- Search history

### Responsive Breakpoints
- Mobile: < 480px
- Tablet: 480px - 768px
- Desktop: > 768px
- Large: > 1024px

## Performance Optimizations

- **Code Splitting**: Lazy loading for non-critical components
- **Bundle Optimization**: Vite's built-in optimizations
- **Image Optimization**: Responsive images and modern formats
- **CSS Optimization**: CSS variables and efficient selectors
- **JavaScript**: Modern ES6+ features with tree shaking

## Accessibility

- **Semantic HTML**: Proper heading hierarchy and landmarks
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Readers**: ARIA labels and descriptions
- **Color Contrast**: WCAG AA compliant color ratios
- **Focus Management**: Visible focus indicators

## Future Enhancements

- **PWA Support**: Service workers and offline functionality
- **Dark/Light Theme**: User-selectable theme preferences
- **Advanced Filters**: More sophisticated search options
- **Data Export**: CSV/PDF export functionality
- **User Accounts**: Saved searches and preferences
- **Push Notifications**: Price alerts and updates

## Contributing

1. Follow the existing code style and patterns
2. Use semantic commit messages
3. Test on multiple screen sizes
4. Ensure accessibility compliance
5. Update documentation for new features
