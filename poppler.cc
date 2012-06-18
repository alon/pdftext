#include <stdio.h>

#include <PDFDocFactory.h>
#include <UnicodeMap.h>
#include <GlobalParams.h>
#include <PDFDocEncoding.h>
#include <DateInfo.h>

GBool xml = 0;

// Cribbed entirely from pdftohtml.cc, in poppler/utils
GooString* HtmlFilter(Unicode* u, int uLen) {
  GooString *tmp = new GooString();
  UnicodeMap *uMap;
  char buf[8];
  int n;

  // get the output encoding
  if (!(uMap = globalParams->getTextEncoding())) {
    return tmp;
  }

  for (int i = 0; i < uLen; ++i) {
    switch (u[i])
      { 
	case '"': tmp->append("&#34;");  break;
	case '&': tmp->append("&amp;");  break;
	case '<': tmp->append("&lt;");  break;
	case '>': tmp->append("&gt;");  break;
	case ' ': tmp->append( !xml && ( i+1 >= uLen || !tmp->getLength() || tmp->getChar( tmp->getLength()-1 ) == ' ' ) ? "&#160;" : " " );
	          break;
	default:  
	  {
	    // convert unicode to string
	    if ((n = uMap->mapUnicode(u[i], buf, sizeof(buf))) > 0) {
	      tmp->append(buf, n); 
	  }
      }
    }
  }

  uMap->decRefCnt();
  return tmp;
}

static GooString* getInfoString(Dict *infoDict, char *key) {
  Object obj;
  // Raw value as read from PDF (may be in pdfDocEncoding or UCS2)
  GooString *rawString;
  // Value converted to unicode
  Unicode *unicodeString;
  int unicodeLength;
  // Value HTML escaped and converted to desired encoding
  GooString *encodedString = NULL;
  // Is rawString UCS2 (as opposed to pdfDocEncoding)
  GBool isUnicode;

  if (infoDict->lookup(key, &obj)->isString()) {
    rawString = obj.getString();

    // Convert rawString to unicode
    if (rawString->hasUnicodeMarker()) {
      isUnicode = gTrue;
      unicodeLength = (obj.getString()->getLength() - 2) / 2;
    } else {
      isUnicode = gFalse;
      unicodeLength = obj.getString()->getLength();
    }
    unicodeString = new Unicode[unicodeLength];

    for (int i=0; i<unicodeLength; i++) {
      if (isUnicode) {
        unicodeString[i] = ((rawString->getChar((i+1)*2) & 0xff) << 8) |
          (rawString->getChar(((i+1)*2)+1) & 0xff);
      } else {
        unicodeString[i] = pdfDocEncoding[rawString->getChar(i) & 0xff];
      }
    }

    // HTML escape and encode unicode
    encodedString = HtmlFilter(unicodeString, unicodeLength);
    delete[] unicodeString;
  }

  obj.free();
  return encodedString;
}

static GooString* getInfoDate(Dict *infoDict, char *key) {
  Object obj;
  char *s;
  int year, mon, day, hour, min, sec, tz_hour, tz_minute;
  char tz;
  struct tm tmStruct;
  GooString *result = NULL;
  char buf[256];

  if (infoDict->lookup(key, &obj)->isString()) {
    s = obj.getString()->getCString();
    // TODO do something with the timezone info
    if ( parseDateString( s, &year, &mon, &day, &hour, &min, &sec, &tz, &tz_hour, &tz_minute ) ) {
      tmStruct.tm_year = year - 1900;
      tmStruct.tm_mon = mon - 1;
      tmStruct.tm_mday = day;
      tmStruct.tm_hour = hour;
      tmStruct.tm_min = min;
      tmStruct.tm_sec = sec;
      tmStruct.tm_wday = -1;
      tmStruct.tm_yday = -1;
      tmStruct.tm_isdst = -1;
      mktime(&tmStruct); // compute the tm_wday and tm_yday fields
      if (strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%S+00:00", &tmStruct)) {
        result = new GooString(buf);
      } else {
        result = new GooString(s);
      }
    } else {
      result = new GooString(s);
    }
  }
  obj.free();
  return result;
}

char *try_cstring(GooString *g)
{
    if (g) {
        return g->getCString();
    }
    return "<null>";
}

int main(int argc, char **argv)
{
    PDFDoc *doc;
    GooString *filename;
    GooString *docTitle, *author, *keywords, *subject, *date;
    Object info;

    if (argc < 2) {
        printf("usage: %s <filename>\n", argv[0]);
        return -1;
    }
    globalParams = new GlobalParams();
    filename = new GooString(argv[1]);

    doc = PDFDocFactory().createPDFDoc(*filename, NULL, NULL);
    printf("okToCopy %d\n", doc->okToCopy());
    printf("");
    doc->getDocInfo(&info);
    if (info.isDict()) {
      docTitle = getInfoString(info.getDict(), (char*)"Title");
      author = getInfoString(info.getDict(), (char*)"Author");
      keywords = getInfoString(info.getDict(), (char*)"Keywords");
      subject = getInfoString(info.getDict(), (char*)"Subject");
      date = getInfoDate(info.getDict(), (char*)"ModDate");
      if( !date )
        date = getInfoDate(info.getDict(), (char*)"CreationDate");
    }
    printf("%s, %s, %s, %s, %s\n",
            try_cstring(docTitle), try_cstring(author), try_cstring(keywords),
            try_cstring(subject), try_cstring(date));
    return 0;
}
