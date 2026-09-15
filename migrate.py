from app import app, db, SiteContent

def run_migration():
    with app.app_context():
        # Create tables (will only create site_content if it doesn't exist)
        db.create_all()
        
        # Seed Data
        seed_data = [
            {
                'id': 'home_about',
                'title': 'The Essence of Our Village',
                'content': "Nestled in the lush landscapes of Nayagarh district, Sankhei is a growing and vibrant village. As you enter, you are welcomed by our primary hospital, a cornerstone of our community's health. We are proud of our educational facilities, offering schooling from standard 1st to 10th to nurture the next generation.\n\nSankhei is a self-sustaining hub, featuring a medium-sized local market that caters to our daily needs. We are also looking forward to the future with the Revenue Inspector (RI) office currently under process, further solidifying our village's infrastructure and development.",
                'image_filename': 'village_temple_1788245881477.png'
            },
            {
                'id': 'home_culture_1',
                'title': 'Vibrant Festivals',
                'content': 'Our biggest celebration is the grand Danda Yatra. We joyously celebrate all major Odia festivals including Raja Parba, Dasahara, and Maha Shiva Ratri, bringing the entire community together in vibrant harmony.',
                'image_filename': 'village_culture_1788245901170.png'
            },
            {
                'id': 'home_culture_2',
                'title': 'Spiritual Roots',
                'content': 'Sankhei is deeply spiritual, blessed by our revered deities. We offer our devotion at the Baba Kapileswar Shiv Temple, Shree Raghunath Mandir, Maa Ramchandi Mandir, Maa Bhairavi Mandir, Maa Khilamunda Mandir, and we also devoutly worship Shani Dev.',
                'image_filename': None
            },
            {
                'id': 'home_culture_3',
                'title': 'Community Life',
                'content': 'The rhythmic, simple lifestyle of our welcoming community is marked by harmony. Every sunrise over our beautiful village brings a new canvas of vibrant earthy colors, painting a picture of togetherness and deep-rooted traditions.',
                'image_filename': None
            }
        ]
        
        for data in seed_data:
            exists = SiteContent.query.get(data['id'])
            if not exists:
                new_content = SiteContent(**data)
                db.session.add(new_content)
                
        db.session.commit()
        print("SiteContent migration and seeding completed.")

if __name__ == "__main__":
    run_migration()
