from blog import app, db, photos, mail

if __name__ == '__main__':
    db.create_all()
    app.run(port=8800, debug=True)
