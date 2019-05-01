classdef Out
    % OUTPUT Prints the solver's information
    
    %% Properties
    properties (SetAccess = private)
        fid;             % File ID obtained after calling fopen
        print2file = 0;  % 1, print the information to a file
        % 0, print in the command window instead
    end
    
    methods
        % Constructor
        function output = Out(fileName)
            if nargin == 0
                output.fid = 1;
            else
                try
                    output.fid = fopen(fileName,'w');
                    output.print2file = 1;
                catch
                    error('PIPM.Output: Failed to open the file to write');
                end
            end
        end
        
        % Display header in the command window or a user provied
        % file
        function printHeader(output, lp, params)
            if params.verbose > 1
                fprintf(output.fid,...
                    '\n========== %s ==========\n\n', lp.Name);
                fprintf(output.fid,...
                    '%4s %9s %9s\n',...
                    'ITER', 'MU', 'RESIDUAL');
            end
        end
        
        % Display ipm iteration information in the command window or
        % a user provied file
        function printIterations(output, iter, params)
            if params.verbose > 1
                fprintf(output.fid, '%4d %9.2e %9.2e\n',...
                    iter.k, iter.mu, iter.residual);
            end
        end
        
        
        % Display footer in the command window or a user provied
        % file
        function printFooter(output, lp, params)
            if params.verbose > 0
                switch lp.status
                    case 0, termMesg = 'Terminated by relative residual';
                    case 1, termMesg = 'Terminated by reaching maxIter';
                    case 2, termMesg = 'Terminated when chol said PD';
                end
                fprintf(output.fid, '======== IPM Done ======== \n');
                fprintf(output.fid,'%s\n', termMesg);
                fprintf(output.fid, 'Function value = %9.2e\n',lp.getFval);
            end
        end
        
    end
    
end
