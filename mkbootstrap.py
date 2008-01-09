#!/usr/bin/env python2.5

import virtualenv, textwrap

if __name__ == '__main__':
    output = virtualenv.create_bootstrap_script(textwrap.dedent("""
        import os, subprocess

        def extend_parser(parser):
            parser.add_option(
                '--simplsale',
                metavar = 'VERSION',
                dest = 'simplsale_version',
                default = 'latest',
                help = '"latest", "manual", or a specific version of SimplSale to install.',
                )

        def after_install(options, home_dir):
            lib = join(home_dir, 'lib')
            # Install libxml2
            cmmi(
                name = 'libxml2',
                prefix = home_dir,
                url = 'ftp://xmlsoft.org/libxml2/libxml2-2.6.30.tar.gz',
                extra_options = ['--without-python'],
                )
            # Install libxslt
            cmmi(
                name = 'libxslt',
                prefix = home_dir,
                url = 'ftp://xmlsoft.org/libxml2/libxslt-1.1.22.tar.gz',
                extra_options = [
                    '--with-libxml-prefix=%s' % home_dir,
                    '--without-python',
                    ],
                )
            # Install SimplSale
            simplsale_version = options.simplsale_version.lower().strip()
            if simplsale_version == 'latest':
                easy_install(home_dir, 'SimplSale')
            elif simplsale_version == 'manual':
                print 'Please now install SimplSale manually.'
            else:
                easy_install(home_dir, 'SimplSale==%s' % simplsale_version)

        def cmmi(name, prefix, url, extra_options):
            import urllib2, tarfile
            # Create workspace to compile in.
            workspace = join(prefix, 'src', name)
            if not os.path.exists(workspace):
                os.makedirs(workspace)
                # Extract the package to the workspace.
                print 'Extracting', url, 'to', workspace
                tar_gz = urllib2.urlopen(url)
                tar = tarfile.TarFile.open(fileobj=tar_gz, mode='r|*')
                tar.extractall(workspace)
                tar.close()
                tar_gz.close()
                # Assume that the only file in the workspace is a directory, and that
                # it is the directory that we want to build within.
                src = join(workspace, os.listdir(workspace)[0])
                os.chdir(src)
                args = [
                    join(src, 'configure'),
                    '--prefix=%s' % prefix,
                    ]
                args.extend(extra_options)
                print ' '.join(args)
                subprocess.call(args)
                print 'make'
                subprocess.call(['make'])
                print 'make install'
                subprocess.call(['make', 'install'])
            else:
                print 'Already extracted', name

        def easy_install(home_dir, package, extra_options):
            options = [join(home_dir, 'bin', 'easy_install')]
            options.extend(extra_options)
            options.append(package)
            subprocess.call(options)
        """))
    f = open('simplsale-bootstrap.py', 'w').write(output)
