// 
// Decompiled by Procyon v0.5.36
// 

package l2f.dm.wiki;

import javax.xml.xpath.XPathExpression;
import org.w3c.dom.Document;
import javax.xml.xpath.XPath;
import javax.xml.parsers.DocumentBuilder;
import org.xml.sax.SAXException;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathConstants;
import org.w3c.dom.NodeList;
import javax.xml.xpath.XPathFactory;
import javax.xml.parsers.DocumentBuilderFactory;
import org.xml.sax.InputSource;
import java.io.ByteArrayInputStream;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.Writer;
import java.io.BufferedWriter;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.FileOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.io.UnsupportedEncodingException;
import java.util.List;
import java.util.ArrayList;
import java.io.Reader;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.FileInputStream;
import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.io.Serializable;
import javax.net.ssl.HttpsURLConnection;
import org.xml.sax.SAXParseException;
import java.text.Normalizer;
import java.io.*;
import java.io.StringWriter;
import java.util.HashMap;

import org.apache.commons.text.StringEscapeUtils;
import org.apache.commons.lang3.StringUtils;

import org.jsoup.Jsoup;
//import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;


public class WikiBot implements Serializable
{
    private Map<String, WikiPage> wikiPageCache;
    private Map<String, String> htmlPageCache;
    private String wikiURL;
    private String wikiPageCachePath;
    private String htmlPageCachePath;
    private int maxWikiSearchResults;
    public static String NORESULTS;
    private static final long serialVersionUID = -1755078279045938299L;
    
    static {
        WikiBot.NORESULTS = "No results found for: ";
    }
    
    public WikiBot(final String wikiURL, final int maxWikiSearchResults, final String wikiPageCachePath, final String htmlPageCachePath) {
        this.wikiPageCache = new HashMap<String, WikiPage>();
        this.htmlPageCache = new HashMap<String, String>();
        this.wikiURL = wikiURL;
        this.maxWikiSearchResults = maxWikiSearchResults;
        this.wikiPageCachePath = wikiPageCachePath;
        this.htmlPageCachePath = htmlPageCachePath;
        this.buildCacheMaps();
        //System.out.println("cheguei aqui");
    }
    
    private void buildCacheMaps() {
        try {
            final File htmlCacheFile = new File(this.htmlPageCachePath);
            if (htmlCacheFile.exists()) {
                final BufferedReader inHTML = new BufferedReader(new InputStreamReader(new FileInputStream(this.htmlPageCachePath), "UTF8"));
                String line;
                while ((line = inHTML.readLine()) != null) {
                    final String[] strArray = line.split("<\\$=\\$>");
                    this.htmlPageCache.put(strArray[0], strArray[1]);
                }
            }
            final File wikiCacheFile = new File(this.wikiPageCachePath);
            List<String> paragraphList = new ArrayList<String>();
            if (wikiCacheFile.exists()) {
                final BufferedReader inHTML2 = new BufferedReader(new InputStreamReader(new FileInputStream(this.wikiPageCachePath), "UTF8"));
                String line;
                while ((line = inHTML2.readLine()) != null) {
                    final String[] strArray = line.split("<\\$=\\$>");
                    final String key = strArray[0];
                    final String[] paragraphs = strArray[1].split("<\\$>");
                    for (int i = 1; i < paragraphs.length; ++i) {
                        paragraphList.add(paragraphs[i]);
                    }
                    this.wikiPageCache.put(key, new WikiPage((List)paragraphList));
                    paragraphList = new ArrayList<String>();
                }
            }
        }
        catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        catch (FileNotFoundException e2) {
            e2.printStackTrace();
        }
        catch (IOException e3) {
            e3.printStackTrace();
        }
    }
    
    public String getHTML(final String urlToRead) {
        //final String cachedPage = this.htmlPageCache.get(urlToRead);
        //if (cachedPage != null) {
            //System.out.println("Using HTMLPage cache for " + urlToRead);
         //   return cachedPage;
        //}
        String result = "";
        try {
            final URL url = new URL(urlToRead);
            final HttpsURLConnection conn = (HttpsURLConnection)url.openConnection();
            final BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String line;
            while ((line = rd.readLine()) != null) {
                result = String.valueOf(result) + line;
            }
            rd.close();
        }
        catch (Exception e) {
            e.printStackTrace();
        }
        result = result.substring(result.indexOf(">") + 1);
        result = result.replaceAll("<a href=\"#cite_note[^>]+>[^<]+</a>", "");
        this.cacheResults(urlToRead, result, this.htmlPageCachePath);
        this.htmlPageCache.put(urlToRead, result);
        //String temp = Normalizer.normalize(result, java.text.Normalizer.Form.NFD);
        //result = temp.replaceAll("[^\\p{ASCII}]","");
        //result = result.replaceAll("[^\\x00-\\x7F]", "");
        //System.out.println(result);
        return result;
    }
    
    private void cacheResults(final String key, final String toCache, final String cacheFilePath) {
        if (toCache.equals("")) {
            return;
        }
        try {
            final BufferedWriter out = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(cacheFilePath, true), "UTF-8"));
            out.write(String.valueOf(key) + "<$=$>" + toCache + "\n");
            out.close();
        }
        catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    public String queryWiki(final String query) {
        String query2 = query.replaceAll("[^\\x00-\\x7F]", "");
        return this.getHTML(String.valueOf(this.wikiURL) + "/w/api.php?action=query&prop=revisions&titles=" + query2 + "&format=xml");
    }
    
    public String openSearchWiki(final String search) {
        String search2 = search.replaceAll("[^\\x00-\\x7F]", "");
        return this.getHTML(String.valueOf(this.wikiURL) + "/w/api.php?action=opensearch&search=" + search2 + "&limit=" + this.maxWikiSearchResults + "&namespace=0&format=xml");
    }
    
    public String parseWiki(final String pageTitle) {
        String pageTitle2 = pageTitle.replaceAll("[^\\x00-\\x7F]", "");
        return this.getHTML(String.valueOf(this.wikiURL) + "/w/api.php?action=parse&page=" + pageTitle2 + "&format=xml");
    }
    
    public String articleSearch(final String search) {
        String search2 = search.replaceAll("[^\\x00-\\x7F]", "");
        return this.getHTML(String.valueOf(this.wikiURL) + "/w/index.php?title=Especial%3APesquisar&profile=default&search=" + search2.replaceAll(" ", "+") + "&fulltext=Search&searchengineselect=mediawiki&ns0=1");
    }
    
    public List<String> getArticleTitle(final String htmlPage) {
        final List<String> articleTiles = new ArrayList<String>();
        final Pattern patt = Pattern.compile("mw-search-result-heading'><a href=\"/wiki/[^\"]*\"");
        final Matcher matcher = patt.matcher(htmlPage);
        while (matcher.find()) {
            String strMatch = matcher.group(0);
            strMatch = strMatch.replaceAll("mw-search-result-heading'><a href=\"/wiki/", "");
            strMatch = strMatch.substring(0, strMatch.length() - 1);
            articleTiles.add(strMatch);
        }
        //System.out.println("ARticle titles" + articleTiles);
        return articleTiles;
    }
    public static HashMap<Character, String> XML_DECIMAL_ENCODING = new HashMap<Character, String>();   static  {       XML_DECIMAL_ENCODING.put('œ', "&#156;");        XML_DECIMAL_ENCODING.put('À', "&#192;");        XML_DECIMAL_ENCODING.put('Ä', "&#196;");        XML_DECIMAL_ENCODING.put('Æ', "&#198;");        XML_DECIMAL_ENCODING.put('Ç', "&#199;");        XML_DECIMAL_ENCODING.put('È', "&#200;");        XML_DECIMAL_ENCODING.put('É', "&#201;");        XML_DECIMAL_ENCODING.put('Ë', "&#203;");        XML_DECIMAL_ENCODING.put('Ï', "&#207;");        XML_DECIMAL_ENCODING.put('Æ', "&#209;");        XML_DECIMAL_ENCODING.put('Ö', "&#214;");        XML_DECIMAL_ENCODING.put('Ü', "&#220;");        XML_DECIMAL_ENCODING.put('à', "&#224;");        XML_DECIMAL_ENCODING.put('â', "&#226;");        XML_DECIMAL_ENCODING.put('ä', "&#228;");        XML_DECIMAL_ENCODING.put('æ', "&#230;");                 XML_DECIMAL_ENCODING.put('ç', "&#231;");       XML_DECIMAL_ENCODING.put('è', "&#232;");        XML_DECIMAL_ENCODING.put('é', "&#233;");        XML_DECIMAL_ENCODING.put('ê', "&#234;");        XML_DECIMAL_ENCODING.put('ë', "&#235;");                 XML_DECIMAL_ENCODING.put('î', "&#238;");       XML_DECIMAL_ENCODING.put('ï', "&#239;");                 XML_DECIMAL_ENCODING.put('ô', "&#244;");       XML_DECIMAL_ENCODING.put('ö', "&#246;");                 XML_DECIMAL_ENCODING.put('ù', "&#249;");       XML_DECIMAL_ENCODING.put('ñ', "&#241;");        XML_DECIMAL_ENCODING.put('ü', "&#252;");        XML_DECIMAL_ENCODING.put('û', "&#251;");    } 

    private List<String> getDesambiguationTitles(final String htmlPage) {
        final List<String> results = new ArrayList<String>();
        /*try {
            //String str = StringUtils.replace(htmlPage, "eacute", "");
            String str = StringEscapeUtils.escapeHtml4(htmlPage);
            //str = "<?xml version=\"1.0\" encoding=\"ISO-....\"><root><name>Veera</name><Age>30</Age></root>";
            str = str.replaceAll("&lt", "<");
            str = str.replaceAll("&gt", ">");
            final InputStream is = new ByteArrayInputStream(str.getBytes());
            final Reader reader = new InputStreamReader(is, "UTF-8");
            final InputSource inStream = new InputSource(reader);
            final DocumentBuilderFactory domFactory = DocumentBuilderFactory.newInstance();
            final DocumentBuilder builder = domFactory.newDocumentBuilder();
            final XPathFactory factory = XPathFactory.newInstance();
            final XPath xpath = factory.newXPath();
            final Document doc = builder.parse(inStream);
            doc.getDocumentElement().normalize();
            final XPathExpression expr = xpath.compile("//div[@id='mw-content-text']/ul/li/a/@href | //div[@id='mw-content-text']/p/a/@href");
            final NodeList qNL = (NodeList)expr.evaluate(doc, XPathConstants.NODESET);
            for (int i = 0; i < qNL.getLength(); ++i) {
                final String nodeStr = qNL.item(i).getTextContent();
                if (!nodeStr.contains("redlink=")) {
                    results.add(nodeStr.replaceAll("/wiki/", ""));
                }
            }
            return results;
        }
        catch (XPathExpressionException e) {
            e.printStackTrace();
        }
        catch (ParserConfigurationException e2) {
            e2.printStackTrace();
        }
        catch (SAXException e3) {
            e3.printStackTrace();
        }
        catch (IOException e4) {
            e4.printStackTrace();
        }
        return null;*/

       
    try {
        org.jsoup.nodes.Document doc = Jsoup.connect(htmlPage).get();

        int count = 0;
        Elements elements = doc.select("span.mw-headline, li > a");
        //System.out.println(elements);
        boolean inPeopleSection = false;
        for (Element elem : elements) {
        //System.out.println(elem);
            if (elem.hasAttr("href")) {
                if (elem.toString().startsWith("<a href=\"/wiki/")){
                    if (elem.toString().contains("title=\"Categoria:Desambiguação\"")) {
                        break;
                    }
                count++;
                results.add(elem.attr("title").replace(" ", "_"));
               //System.out.println("https://pt.wikipedia.org/wiki/"+elem.attr("title").replace(" ", "_"));
                //Document doc2 = Jsoup.connect("https://pt.wikipedia.org/wiki/"+ elem.attr("title").replace(" ", "_")).get();
                //System.out.println(doc2);
                }
            }
        }
        //System.out.println(count);
    } catch (Exception e) {
        e.printStackTrace();
    }
    return results;

}


        private boolean isDesambiguationPage(String htmlPage) {
            
        //try {
            if (htmlPage.contains("id=\"disambig\""))
                return true;
            else
                return false;
            //System.out.println(htmlPage);

            /*String str = StringUtils.replace(htmlPage, "eacute", "");
            str = StringEscapeUtils.escapeHtml4(str);
            //str = "<?xml version=\"1.0\" encoding=\"ISO-....\"><root><name>Veera</name><Age>30</Age></root>";
            str = str.replaceAll("&lt", "<");
            str = str.replaceAll("&gt", ">");

            //System.out.println(str);
            InputStream is = new ByteArrayInputStream(str.getBytes());
            Reader reader = new InputStreamReader(is);
            InputSource inStream = new InputSource(reader);


            
            //Reader reader2 = inStream.getCharacterStream();
            //String result = convert(inStream.getCharacterStream(), "UTF-8");

            //System.out.println(result);
            //StringEscapeUtils sesc = new StringEscapeUtils();
            //String str = StringEscapeUtils.unescapeHtml4(result);

            //InputSource inputSource = new InputSource( new StringReader( str ) );

            DocumentBuilderFactory domFactory = DocumentBuilderFactory.newInstance();
            //domFactory.isReplacingEntityReferences(false);
            DocumentBuilder builder = domFactory.newDocumentBuilder();
            Document doc;
            //Document document = builder.parse(new File( htmlPage ));

            XPathFactory factory = XPathFactory.newInstance();
            XPath xpath = factory.newXPath();

            XPathExpression expr;
            doc = builder.parse(inStream);
            doc.getDocumentElement().normalize();

            expr = xpath.compile("//div[@id='disambig']");
            NodeList qNL = (NodeList)expr.evaluate(doc, XPathConstants.NODESET);
            return qNL.getLength() >= 1;
        } catch (XPathExpressionException e) {
            e.printStackTrace();
        } catch (ParserConfigurationException e) {
            e.printStackTrace();
        } catch (SAXException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return false;*/
    }
    
    public WikiPage getWikiPage(final String query) {
        //final WikiPage cachedQuery = this.wikiPageCache.get(query);
        //System.out.println("cached query: " + cachedQuery);
        //if (cachedQuery != null) {
         //   return cachedQuery;
        //}
        final String possibleArticlesHTML = this.articleSearch(query);
        final List<String> paragraphs = new ArrayList<String>();
        final List<String> results = this.getArticleTitle(possibleArticlesHTML);
        if (results.size() == 0) {
            paragraphs.add(String.valueOf(WikiBot.NORESULTS) + query);
            return new WikiPage((List)paragraphs);
        }
        //System.out.println("URL - > " + String.valueOf(this.wikiURL) + "/wiki/" + results.get(0));
        String url = String.valueOf(this.wikiURL) + "/wiki/" + results.get(0);
        String wikiPageHTML = this.getHTML(String.valueOf(this.wikiURL) + "/wiki/" + results.get(0));
        String temp = Normalizer.normalize(wikiPageHTML, java.text.Normalizer.Form.NFD);
        wikiPageHTML = temp.replaceAll("[^\\p{ASCII}]","");
        wikiPageHTML = wikiPageHTML.replaceAll("[^\\x00-\\x7F]", "");
        //System.out.println(wikiPageHTML);

        int searchResultsIndex = 1;
        while (this.isDesambiguationPage(wikiPageHTML)) {
            //System.out.println()
            final List<String> desambiguationTitlesList = this.getDesambiguationTitles(String.valueOf(this.wikiURL) + "/wiki/" + results.get(0));
            if (desambiguationTitlesList.size() == 0) {
                wikiPageHTML = this.getHTML(String.valueOf(this.wikiURL) + "/wiki/" + results.get(searchResultsIndex));
                ++searchResultsIndex;
            }
            else {
                wikiPageHTML = this.getHTML(String.valueOf(this.wikiURL) + "/wiki/" + desambiguationTitlesList.get(0));
            }
        }
        /*try {
            String str = StringUtils.replace(wikiPageHTML, "eacute", "");
            str = StringEscapeUtils.escapeHtml4(str);
            str = str.replaceAll("&lt", "<");
            str = str.replaceAll("&gt", ">");
            final InputStream is = new ByteArrayInputStream(str.getBytes());
            final Reader reader = new InputStreamReader(is, "UTF-8");
            final InputSource inStream = new InputSource(reader);
            final DocumentBuilderFactory domFactory = DocumentBuilderFactory.newInstance();
            final DocumentBuilder builder = domFactory.newDocumentBuilder();
            final XPathFactory factory = XPathFactory.newInstance();
            final XPath xpath = factory.newXPath();
            final org.w3c.dom.Document doc = builder.parse(inStream);
            doc.getDocumentElement().normalize();
            final XPathExpression rExpr = xpath.compile("//div/p/small");
            final NodeList rNL = (NodeList)rExpr.evaluate(doc, XPathConstants.NODESET);
            XPathExpression expr = xpath.compile("//div[@id='mw-content-text' or @class='mw-content-ltr']/p");
            NodeList qNL = (NodeList)expr.evaluate(doc, XPathConstants.NODESET);
            String strParagraphs = "";
            for (int i = 0; i < qNL.getLength(); ++i) {
                String node = qNL.item(i).getTextContent();
                for (int j = 0; j < rNL.getLength(); ++j) {
                    node = node.replaceAll(rNL.item(j).getTextContent(), "");
                }
                if (!node.equals("")) {
                    paragraphs.add(node);
                    strParagraphs = String.valueOf(strParagraphs) + "<$>" + node;
                }
            }
            if (paragraphs.size() == 0) {
                expr = xpath.compile("//div[@class='mw-content-ltr']/div[@class='noprint']/p");
                qNL = (NodeList)expr.evaluate(doc, XPathConstants.NODESET);
                for (int i = 0; i < qNL.getLength(); ++i) {
                    String node = qNL.item(i).getTextContent();
                    for (int j = 0; j < rNL.getLength(); ++j) {
                        node = node.replaceAll(rNL.item(j).getTextContent(), "");
                    }
                    if (!node.equals("")) {
                        paragraphs.add(node);
                        strParagraphs = String.valueOf(strParagraphs) + "<$>" + node;
                    }
                }
            }*/

        try{
            org.jsoup.nodes.Document doc = Jsoup.connect(String.valueOf(this.wikiURL) + "/wiki/" + results.get(0)).get();
            Elements paragraphss = doc.select(".mw-content-ltr p");

            Element firstParagraph = paragraphss.first();
            Element lastParagraph = paragraphss.last();
            Element p;
            int i=1;
            p=firstParagraph;
            String strParagraphs = "";
            //System.out.println(p.text());
            while (p!=lastParagraph){
                p=paragraphss.get(i);
                strParagraphs += p.text();
                paragraphs.add(p.text());
                //System.out.println(p.text());
                i++;
            } 
            if (paragraphs.size() == 0) {
                paragraphs.add(String.valueOf(WikiBot.NORESULTS) + query);
                return new WikiPage((List)paragraphs);
            }
            final WikiPage wp = new WikiPage((List)paragraphs);
            this.cacheResults(query, strParagraphs, this.wikiPageCachePath);
            this.wikiPageCache.put(query, wp);
            return wp;
        }
        catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }


    


}


