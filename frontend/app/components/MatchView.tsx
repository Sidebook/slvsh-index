import moment from "moment";

interface Props {
  title: string;
  who?: string;
  upload_date: string;
  video_id: string;
}

const formatDate = (date: string) => {
  const m = moment(date);
  return `${m.format("YYYY/MM/DD")} - ${m.fromNow()}`;
};

const MatchView: React.FC<Props> = (props) => {
  const who = props.who?.toLowerCase();
  let parts: string[] = [props.title];
  if (who) {
    const index = props.title.toLowerCase().indexOf(who);
    parts = [
      props.title.slice(0, index),
      props.title.slice(index, index + who.length),
      props.title.slice(index + who.length),
    ];
  }

  return (
    <div className="flex flex-row items-center">
      <div className="mr-4">
        <img
          src={`https://img.youtube.com/vi/${props.video_id}/mqdefault.jpg`}
          alt={`Thumbnail for ${props.title}`}
          className="w-32 h-18 object-cover rounded-md"
        />
      </div>
      <div className="text-xl flex-1">
        {parts.map((part, index) => (
          <span
            key={index}
            className={part.toLowerCase() === who?.toLowerCase() ? "match" : ""}
          >
            {part}
          </span>
        ))}
        <div className="text-sm text-gray-500">
          {formatDate(props.upload_date)}
        </div>
      </div>
    </div>
  );
};

export default MatchView;
