<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tm="http://www.wipo.int/standards/XMLSchema/trademarks" xmlns:pto="urn:us:gov:doc:uspto:trademark:status">
<xsl:output method="text" encoding="utf-8"/>
<xsl:template match="tm:Transaction">
<xsl:apply-templates select=".//tm:TradeMark"/>
</xsl:template>
<xsl:template match="tm:TradeMark">
<xsl:text/>ApplicationNumber,"<xsl:value-of select="tm:ApplicationNumber"/>"<xsl:text/>
PublicationDate,"<xsl:value-of select="tm:PublicationDetails/tm:Publication/tm:PublicationDate"/>"<xsl:text/>
</xsl:template>
</xsl:stylesheet>