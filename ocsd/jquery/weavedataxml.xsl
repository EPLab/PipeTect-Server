<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <style>
	  td {color:#000000}
	  th {color:#000000; background-color:#cccccc}
  </style>
    <h2>WeaveData Result</h2>
    <table border="1">
    <tr>
      <xsl:for-each select="ResultSet/MetaData/Column">
        <th><xsl:value-of select="@name"/></th>
      </xsl:for-each>
    </tr>
    <xsl:for-each select="ResultSet/Data/Row">
      <tr>
        <xsl:for-each select="Cell">
          <td><xsl:value-of select="@value"/></td>
        </xsl:for-each>
      </tr>
    </xsl:for-each>
    </table>
</xsl:template>
</xsl:stylesheet>