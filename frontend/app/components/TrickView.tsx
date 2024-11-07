import React from "react";
import { Trick } from "../types/trick";

interface Props {
  trick: Trick;
  what: string;
  className?: string;
}

const formatTimestamp = (timestamp: number) => {
  const date = new Date(timestamp * 1000);
  return `${date.getMinutes()}:${date
    .getSeconds()
    .toString()
    .padStart(2, "0")}`;
};

const tokenize = (text: string) => {
  return text
    .replaceAll(",", " ")
    .split(" ")
    .map((token) => token.toLowerCase());
};

const isMatch = (component: string, query: string) => {
  if (query === "") {
    return false;
  }
  const componentTokens = tokenize(component);
  const queryTokens = tokenize(query);
  return queryTokens.every((token) => componentTokens.includes(token));
};

const TrickView: React.FC<Props> = (props) => {
  return (
    <div className={`${props.className} flex`}>
      <div className="font-bold mr-3 min-w-[3rem]">
        {formatTimestamp(props.trick.start)}
      </div>
      <a
        href={props.trick.url}
        target="_blank"
        rel="noopener noreferrer"
        className="no-underline"
      >
        {props.trick.components.map((component, i) => {
          const matching = isMatch(component, props.what);
          return (
            <span key={`${component}-${i}`}>
              <span className={matching ? "match" : ""}>{component}</span>
              {i < props.trick.components.length - 1 && (
                <span className="mx-2">›</span>
              )}
            </span>
          );
        })}
      </a>
    </div>
  );
};

export default TrickView;
