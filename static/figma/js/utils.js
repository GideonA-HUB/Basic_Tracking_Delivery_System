/**
 * Utility functions for Figma design system
 * Converted from React utils.tsx to vanilla JavaScript
 */

/**
 * Combines class names using clsx and tailwind-merge logic
 * @param {...(string|object|Array)} inputs - Class names to combine
 * @returns {string} - Combined class names
 */
function cn(...inputs) {
  // Simple implementation of clsx + tailwind-merge
  const classes = [];
  
  for (const input of inputs) {
    if (!input) continue;
    
    if (typeof input === 'string') {
      classes.push(input);
    } else if (Array.isArray(input)) {
      classes.push(cn(...input));
    } else if (typeof input === 'object') {
      for (const [key, value] of Object.entries(input)) {
        if (value) {
          classes.push(key);
        }
      }
    }
  }
  
  return classes.join(' ');
}

/**
 * Formats a date to a readable string
 * @param {Date|string} date - Date to format
 * @param {object} options - Formatting options
 * @returns {string} - Formatted date string
 */
function formatDate(date, options = {}) {
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options
  };
  
  return new Intl.DateTimeFormat('en-US', defaultOptions).format(new Date(date));
}

/**
 * Formats a number as currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code
 * @returns {string} - Formatted currency string
 */
function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
}

/**
 * Debounces a function call
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttles a function call
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} - Throttled function
 */
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Checks if element is in viewport
 * @param {Element} element - Element to check
 * @returns {boolean} - True if element is in viewport
 */
function isInViewport(element) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

/**
 * Smooth scroll to element
 * @param {string|Element} target - Target element or selector
 * @param {object} options - Scroll options
 */
function scrollToElement(target, options = {}) {
  const element = typeof target === 'string' ? document.querySelector(target) : target;
  if (!element) return;
  
  const defaultOptions = {
    behavior: 'smooth',
    block: 'start',
    ...options
  };
  
  element.scrollIntoView(defaultOptions);
}

/**
 * Gets or sets a cookie
 * @param {string} name - Cookie name
 * @param {string} value - Cookie value (optional)
 * @param {object} options - Cookie options
 * @returns {string|null} - Cookie value or null
 */
function cookie(name, value, options = {}) {
  if (value === undefined) {
    // Get cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [cookieName, cookieValue] = cookie.trim().split('=');
      if (cookieName === name) {
        return decodeURIComponent(cookieValue);
      }
    }
    return null;
  } else {
    // Set cookie
    let cookieString = `${name}=${encodeURIComponent(value)}`;
    
    if (options.expires) {
      const date = new Date();
      date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
      cookieString += `; expires=${date.toUTCString()}`;
    }
    
    if (options.path) {
      cookieString += `; path=${options.path}`;
    }
    
    if (options.domain) {
      cookieString += `; domain=${options.domain}`;
    }
    
    if (options.secure) {
      cookieString += '; secure';
    }
    
    if (options.sameSite) {
      cookieString += `; samesite=${options.sameSite}`;
    }
    
    document.cookie = cookieString;
  }
}

/**
 * Local storage helpers
 */
const storage = {
  get: (key) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  },
  
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch {
      return false;
    }
  },
  
  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch {
      return false;
    }
  }
};

/**
 * Event emitter for component communication
 */
class EventEmitter {
  constructor() {
    this.events = {};
  }
  
  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }
  
  off(event, callback) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter(cb => cb !== callback);
  }
  
  emit(event, ...args) {
    if (!this.events[event]) return;
    this.events[event].forEach(callback => callback(...args));
  }
}

/**
 * Animation helpers
 */
const animations = {
  fadeIn: (element, duration = 300) => {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease-in-out`;
    requestAnimationFrame(() => {
      element.style.opacity = '1';
    });
  },
  
  fadeOut: (element, duration = 300) => {
    element.style.transition = `opacity ${duration}ms ease-in-out`;
    element.style.opacity = '0';
    setTimeout(() => {
      element.style.display = 'none';
    }, duration);
  },
  
  slideIn: (element, direction = 'up', duration = 300) => {
    const transforms = {
      up: 'translateY(20px)',
      down: 'translateY(-20px)',
      left: 'translateX(20px)',
      right: 'translateX(-20px)'
    };
    
    element.style.transform = transforms[direction];
    element.style.opacity = '0';
    element.style.transition = `transform ${duration}ms ease-out, opacity ${duration}ms ease-out`;
    
    requestAnimationFrame(() => {
      element.style.transform = 'translate(0, 0)';
      element.style.opacity = '1';
    });
  }
};

/**
 * Form validation helpers
 */
const validation = {
  email: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },
  
  phone: (phone) => {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone.replace(/[\s\-\(\)]/g, ''));
  },
  
  required: (value) => {
    return value && value.toString().trim().length > 0;
  },
  
  minLength: (value, min) => {
    return value && value.toString().length >= min;
  },
  
  maxLength: (value, max) => {
    return value && value.toString().length <= max;
  }
};

/**
 * API helpers
 */
const api = {
  request: async (url, options = {}) => {
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': cookie('csrftoken') || ''
      }
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  },
  
  get: (url, options = {}) => {
    return api.request(url, { ...options, method: 'GET' });
  },
  
  post: (url, data, options = {}) => {
    return api.request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  
  put: (url, data, options = {}) => {
    return api.request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },
  
  delete: (url, options = {}) => {
    return api.request(url, { ...options, method: 'DELETE' });
  }
};

// Export utilities for use in other scripts
window.FigmaUtils = {
  cn,
  formatDate,
  formatCurrency,
  debounce,
  throttle,
  isInViewport,
  scrollToElement,
  cookie,
  storage,
  EventEmitter,
  animations,
  validation,
  api
};
