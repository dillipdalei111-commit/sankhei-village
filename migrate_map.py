from app import app, db, MapLocation

def run_migration():
    with app.app_context():
        # Create tables (will only create map_location if it doesn't exist)
        db.create_all()
        
        # Check if locations already exist
        if MapLocation.query.count() == 0:
            seed_data = [
                {
                    'name': 'Baba Kapileswar Shiv Temple',
                    'description': 'The central shrine.',
                    'latitude': 20.1226,
                    'longitude': 85.1054,
                    'icon_type': 'temple'
                },
                {
                    'name': 'Primary Hospital',
                    'description': 'Located at the village entrance.',
                    'latitude': 20.1250,
                    'longitude': 85.1020,
                    'icon_type': 'default'
                },
                {
                    'name': 'High School',
                    'description': 'Standard 1st to 10th.',
                    'latitude': 20.1200,
                    'longitude': 85.1080,
                    'icon_type': 'default'
                },
                {
                    'name': 'Village Market',
                    'description': 'Medium market area.',
                    'latitude': 20.1240,
                    'longitude': 85.1090,
                    'icon_type': 'default'
                },
                {
                    'name': 'Maa Ramchandi Mandir',
                    'description': '',
                    'latitude': 20.1210,
                    'longitude': 85.1030,
                    'icon_type': 'temple'
                },
                {
                    'name': 'RI Office',
                    'description': 'Revenue Inspector Office (Under process).',
                    'latitude': 20.1260,
                    'longitude': 85.1060,
                    'icon_type': 'default'
                }
            ]
            
            for data in seed_data:
                new_loc = MapLocation(**data)
                db.session.add(new_loc)
                    
            db.session.commit()
            print("MapLocation migration and seeding completed.")
        else:
            print("MapLocations already seeded.")

if __name__ == "__main__":
    run_migration()
