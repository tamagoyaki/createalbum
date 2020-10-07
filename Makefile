PHOTO_DIR = ./
EXT = JPG

help:
	@echo 'make check-ext'
	@echo 'make list > list.createalbum'


check-ext:
	@find . -type f | sed 's/.*\(...\)/\1/' | sort | uniq

TOALBUM = sed 's/$$/, 0,/'
TOSJISDOS = nkf -s -Lw -c

# as an example
list:
	@{ \
		for file in `find . -iname "*.$(EXT)"`; do\
			comment=`echo $$file | awk -F/ '{print $$2","$$3","$$4","$$5","$$6}' | sed 's/,[^,]*\.[jJ][pP][gG]//'` ; \
			wslpath -w $$file | sed "s/$$/, 0, $$comment/" | $(TOSJISDOS) ; \
		done; \
	}
