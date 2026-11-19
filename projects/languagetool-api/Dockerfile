FROM docker.io/library/eclipse-temurin:21-jre

ARG LT_VERSION=6.6

WORKDIR /opt/languagetool

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl unzip && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fSL \
    "https://languagetool.org/download/LanguageTool-${LT_VERSION}.zip" \
    -o /tmp/languagetool.zip && \
    unzip /tmp/languagetool.zip -d /tmp && \
    mv "/tmp/LanguageTool-${LT_VERSION}"/* /opt/languagetool/ && \
    rm -rf /tmp/languagetool.zip "/tmp/LanguageTool-${LT_VERSION}"

# COPY server.properties /opt/languagetool/server.properties

# RUN mkdir -p /opt/languagetool/dictionaries
# COPY dictionaries/ /opt/languagetool/dictionaries/

EXPOSE 8010

ENV JAVA_OPTS="-Xms512m -Xmx1g"

# CMD ["sh", "-c", "exec java $JAVA_OPTS -cp languagetool-server.jar org.languagetool.server.HTTPServer --config server.properties --port 8010 --public"]

CMD ["sh", "-c", "exec java $JAVA_OPTS -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8010 --public"]