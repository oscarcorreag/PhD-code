package unimelb.edu.au.ridesharing.adapters;

import android.content.Context;
import android.support.annotation.LayoutRes;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.text.DateFormat;
import java.util.List;
import java.util.Locale;

import unimelb.edu.au.ridesharing.R;
import unimelb.edu.au.ridesharing.model.Session;

public class SessionsAdapter extends ArrayAdapter<Session> {

    private final Context mContext;
    private final int mResource;
    private final List<Session> mSessions;

    public SessionsAdapter(@NonNull Context context, @LayoutRes int resource, @NonNull List<Session> sessions) {
        super(context, resource, sessions);

        mContext = context;
        mResource = resource;
        mSessions = sessions;
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {

        View view = convertView;

        if (view == null) {
            view = LayoutInflater.from(mContext).inflate(mResource, parent, false);
        }

        Session session = mSessions.get(position);

        TextView timeCityTextView = view.findViewById(R.id.time_city_textView);
        timeCityTextView.setText(String.format(Locale.getDefault(),
                "%s: %s",
                DateFormat.getDateTimeInstance().format(session.getStartTime()),
                session.getCity()));

        TextView usersTextView = view.findViewById(R.id.users_textView);
        usersTextView.setText(String.format(Locale.getDefault(),
                "Real: %d\tSimulated: %d",
                session.getRealUsers(),
                session.getSimulatedUsers()));

        TextView createdByTextView = view.findViewById(R.id.created_by_textView);
        createdByTextView.setText(String.format(Locale.getDefault(),
                "Created by %d",
                session.getCreator()));

        return view;
    }
}
