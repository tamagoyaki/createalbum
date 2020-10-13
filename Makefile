SRCDIR = ./
REGEXT = [jJ][pP][gG]

help:
	@echo 'make check-ext'
	@echo 'make list | nkf -s -Lw -c > list.createalbum'

check-ext:
	@find $(SRCDIR) -type f | sed 's/.*\(...\)/\1/' | sort | uniq

# as an example
list:
	{ \
		for file in `find $(SRCDIR) -iname "*.$(REGEXT)"`; do\
			comment=`echo $$file | sed 's/\//,/g;s/,[^,]*\.$(REGEXT)//'` ; \
			wslpath -w $$file | sed "s/$$/, 0, $$comment/" ; \
		done; \
	}
