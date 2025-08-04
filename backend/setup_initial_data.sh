#!/bin/bash

# Initial Data Setup Script
# This script helps you set up initial data for the Sufob-Wagtail-Nextjs-Headless project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the backend directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the backend directory."
    exit 1
fi

# Function to show help
show_help() {
    echo "Initial Data Setup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup     Create initial data (default)"
    echo "  clear     Clear all initial data"
    echo "  reset     Clear data and create new initial data"
    echo "  migrate   Run database migrations only"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Create initial data"
    echo "  $0 clear    # Clear all data"
    echo "  $0 reset    # Reset all data"
    echo ""
}

# Function to run migrations
run_migrations() {
    print_status "Running database migrations..."
    python manage.py migrate
    print_success "Migrations completed successfully"
}

# Function to create initial data
create_data() {
    print_status "Creating initial data..."
    python manage.py create_initial_data
    print_success "Initial data created successfully"
    
    echo ""
    print_status "Default user accounts created:"
    echo "  - admin (superuser): admin / admin123"
    echo "  - editor: editor / password123"
    echo "  - author: author / password123"
    echo "  - viewer: viewer / password123"
    echo ""
    print_warning "Please change default passwords in production!"
}

# Function to clear data
clear_data() {
    print_warning "This will delete all initial data!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Clearing initial data..."
        python manage.py clear_initial_data --confirm
        print_success "Data cleared successfully"
    else
        print_status "Operation cancelled"
    fi
}

# Function to reset data
reset_data() {
    print_warning "This will delete all data and create new initial data!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Resetting data..."
        python manage.py clear_initial_data --confirm
        python manage.py create_initial_data
        print_success "Data reset completed successfully"
        
        echo ""
        print_status "Default user accounts created:"
        echo "  - admin (superuser): admin / admin123"
        echo "  - editor: editor / password123"
        echo "  - author: author / password123"
        echo "  - viewer: viewer / password123"
        echo ""
        print_warning "Please change default passwords in production!"
    else
        print_status "Operation cancelled"
    fi
}

# Main logic
case "${1:-setup}" in
    "setup")
        run_migrations
        create_data
        ;;
    "clear")
        clear_data
        ;;
    "reset")
        run_migrations
        reset_data
        ;;
    "migrate")
        run_migrations
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

print_success "Script completed successfully!"
