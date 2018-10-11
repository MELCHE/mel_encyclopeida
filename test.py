import googleDriveCleaner

contents = open('mass_export.html', 'r').read()
template = open('article_template.html', 'r').read()
cleaned = googleDriveCleaner.googleDriveCleaner(contents, template)
f = open('mass_export_clean.html', 'w')
f.write(cleaned)
f.close()
