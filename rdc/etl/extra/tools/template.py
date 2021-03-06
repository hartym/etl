from paste.script.templates import Template, var

vars = [
    var('version', '0.1'),
    var('description', 'ETL Project'),
    var('long_description', 'This project was autogenerated by {0}.'.format(__package__)),
    var('keywords', 'Space-separated keywords/tags'),
    var('author', 'Author name'),
    var('author_email', 'Author email'),
    var('url', 'URL of homepage'),
    var('license_name', 'License name'),
    var('zip_safe', 'True/False: if the package can be distributed as a .zip file',
        default=False),
]

class ETLProjectTemplate(Template):
    _template_dir = 'templates/project'
    summary = 'ETL Project'
    vars = vars